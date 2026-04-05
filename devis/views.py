from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from num2words import num2words
from weasyprint import HTML
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory

from .models import Client, Rapport
from .forms import RapportForm

import devis
import maintenance
from maintenance.models import Maintenance
from .models import Devis, LigneDevis, SectionDevis
from .forms import DevisForm, SectionForm, LigneFormSet
from eau.models import Entreprise
from django.contrib.staticfiles import finders
from django.db import transaction


@login_required
def devis_create(request, pk=None):
    if pk:
        devis = get_object_or_404(Devis, pk=pk)
    else:
        devis = None

    if request.method == "POST":
        if devis:
            devis.client_id = request.POST.get("client")
            devis.objet = request.POST.get("objet")
            devis.date_validite = request.POST.get("date_validite")
            devis.save()
            devis.sections.all().delete()  # reset
        else:
            devis = Devis.objects.create(
                client_id=request.POST.get("client"),
                objet=request.POST.get("objet"),
                date_validite=request.POST.get("date_validite"),
            )

        import re
        sections = {}

        for key, value in request.POST.items():
            match = re.match(r"sections-(\d+)-lignes-(\d+)-(.+)", key)
            if match:
                s_idx, l_idx, field = match.groups()
                sections.setdefault(s_idx, {}).setdefault(l_idx, {})[field] = value

        for s_idx, lignes in sections.items():
            titre = request.POST.get(f"sections-{s_idx}-titre")

            section = SectionDevis.objects.create(
                devis=devis,
                titre=titre,
                ordre=int(s_idx)
            )

            for ligne in lignes.values():
                LigneDevis.objects.create(
                    section=section,
                    designation=ligne.get("designation"),
                    prix_unitaire=ligne.get("pu") or 0,
                    quantite=ligne.get("qte") or 1,
                )

        devis.update_total()

        return redirect("devis_list")
    
    form = DevisForm(instance=devis)
    return render(request, "devis/devis_form.html", {
        "form": form,
        "devis": devis
    })


@login_required
def devis_delete(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    if request.method == "POST":
        devis.delete()
        return redirect('devis_list')
    return render(request, 'devis/devis_confirm_delete.html', {'devis': devis})

def generate_pdf(request, pk):
    """Génération PDF avec montant en lettres"""
    # 1. Récupération des données
    devis = get_object_or_404(Devis, pk=pk)
    entreprise = Entreprise.objects.first()
    logo_path = finders.find('logo.png')

    # 2. Conversion du montant en lettres
    # On convertit en int pour éviter les centimes, puis en majuscules
    total_lettres = num2words(int(devis.total_ht), lang='fr').upper()
    
    # 3. Rendu du template avec le contexte mis à jour
    html_string = render_to_string('devis/pdf_template.html', {
        'devis': devis,
        'entreprise': entreprise,
        'sections': devis.sections.all(),
        'logo_path': logo_path,
        'total_lettres': total_lettres,  # <--- NE PAS OUBLIER CETTE LIGNE
    })

    # 4. Génération du PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    # 5. Réponse
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Devis_{devis.reference}.pdf"'
    return response


from django.db.models import Q, Sum
from django.views.generic import ListView, DetailView

# --- 1. LISTE DES DEVIS (AVEC RECHERCHE ET FILTRE) ---
@login_required
def devis_list(request):
    """Affiche la liste des devis avec barre de recherche"""
    query = request.GET.get('q')
    statut_filter = request.GET.get('statut')
    
    devis_all = Devis.objects.all().select_related('client')

    # Logique de recherche (par référence ou nom du client)
    if query:
        devis_all = devis_all.filter(
            Q(reference__icontains=query) | 
            Q(client__nom__icontains=query) |
            Q(objet__icontains=query)
        )
    
    # Filtre par statut
    if statut_filter:
        devis_all = devis_all.filter(statut=statut_filter)

    return render(request, 'devis/devis_list.html', {
        'devis_list': devis_all,
        'query': query,
        'statut_filter': statut_filter
    })

# --- 2. DÉTAIL DU DEVIS (VISUALISATION DASHBOARD) ---
@login_required
def devis_detail(request, pk):
    """Affiche le détail d'un devis avant export PDF"""
    devis = get_object_or_404(Devis.objects.prefetch_related('sections__lignes'), pk=pk)
    return render(request, 'devis/devis_detail.html', {
        'devis': devis,
        'sections': devis.sections.all()
    })

# --- 3. MISE À JOUR RAPIDE DU STATUT ---
@login_required
def update_devis_status(request, pk, status):
    """Permet de passer un devis en 'Accepté' ou 'Refusé' en un clic"""
    devis = get_object_or_404(Devis, pk=pk)
    if status in dict(Devis.STATUTS):
        devis.statut = status
        devis.save()
        messages.success(request, f"Le statut du devis {devis.reference} a été mis à jour.")
    return redirect('devis_detail', pk=pk)






from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Devis, LigneDevis, SectionDevis
from .forms import DevisForm
import json
import re


@login_required
def devis_update(request, pk):
    """Vue dédiée à la modification d'un devis existant"""
    devis = get_object_or_404(Devis, pk=pk)

    if request.method == "POST":
        # Mettre à jour les informations principales du devis
        devis.client_id = request.POST.get("client")
        devis.objet = request.POST.get("objet")
        devis.date_validite = request.POST.get("date_validite")
        devis.save()
        
        # Supprimer toutes les anciennes sections et lignes (reset complet)
        devis.sections.all().delete()
        
        # Structure pour organiser les données POST
        sections_dict = {}
        
        # Parcourir tous les champs POST pour extraire les sections et lignes
        for key, value in request.POST.items():
            # Pattern pour les titres des sections: sections-0-titre, sections-1-titre, etc.
            titre_match = re.match(r'sections-(\d+)-titre', key)
            if titre_match:
                section_index = titre_match.group(1)
                if section_index not in sections_dict:
                    sections_dict[section_index] = {'titre': value, 'lignes': {}}
                else:
                    sections_dict[section_index]['titre'] = value
                continue
            
            # Pattern pour les lignes: sections-0-lignes-0-designation, etc.
            ligne_match = re.match(r'sections-(\d+)-lignes-(\d+)-(.+)', key)
            if ligne_match:
                section_index = ligne_match.group(1)
                ligne_index = ligne_match.group(2)
                field_name = ligne_match.group(3)
                
                # Initialiser la section si elle n'existe pas
                if section_index not in sections_dict:
                    sections_dict[section_index] = {'titre': '', 'lignes': {}}
                
                # Initialiser la ligne si elle n'existe pas
                if ligne_index not in sections_dict[section_index]['lignes']:
                    sections_dict[section_index]['lignes'][ligne_index] = {}
                
                # Ajouter la valeur du champ
                sections_dict[section_index]['lignes'][ligne_index][field_name] = value
        
        # Sauvegarder les sections et leurs lignes
        for section_index, section_data in sections_dict.items():
            titre = section_data.get('titre', '').strip()
            
            # Ne créer la section que si elle a un titre
            if titre:
                section = SectionDevis.objects.create(
                    devis=devis,
                    titre=titre,
                    ordre=int(section_index)
                )
                
                # Sauvegarder les lignes de cette section
                for ligne_data in section_data['lignes'].values():
                    designation = ligne_data.get('designation', '').strip()
                    
                    # Ne créer la ligne que si elle a une désignation
                    if designation:
                        try:
                            pu = float(ligne_data.get('pu', 0))
                        except (ValueError, TypeError):
                            pu = 0
                        
                        try:
                            qte = float(ligne_data.get('qte', 1))
                        except (ValueError, TypeError):
                            qte = 1
                        
                        unite = ligne_data.get('unite', 'u')
                        
                        LigneDevis.objects.create(
                            section=section,
                            designation=designation,
                            unite=unite,
                            prix_unitaire=pu,
                            quantite=qte,
                        )
        
        # Mettre à jour le total du devis
        devis.update_total()
        
        messages.success(request, f"Le devis {devis.reference} a été modifié avec succès.")
        return redirect("devis_detail", pk=devis.pk)
    
    # Mode GET - Préparer le formulaire avec les données existantes
    form = DevisForm(instance=devis)
    
    # Préparer les données JSON pour pré-remplir le formulaire
    devis_data = []
    for section in devis.sections.all().order_by('ordre'):
        lignes = []
        for ligne in section.lignes.all():
            lignes.append({
                'designation': ligne.designation,
                'unite': ligne.unite,
                'prix_unitaire': float(ligne.prix_unitaire),
                'quantite': float(ligne.quantite),
            })
        devis_data.append({
            'titre': section.titre,
            'lignes': lignes
        })
    
    return render(request, "devis/devis_update.html", {
        "form": form,
        "devis": devis,
        "devis_data": json.dumps(devis_data)
    })









from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Client
from .forms import ClientForm

# Liste et Recherche
def client_list(request):
    query = request.GET.get('q')
    if query:
        clients = Client.objects.filter(
            Q(nom__icontains=query) | Q(email__icontains=query) | Q(telephone__icontains=query)
        )
    else:
        clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients, 'query': query})

# Création
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le client a été ajouté avec succès.")
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'clients/client_form.html', {'form': form, 'title': "Ajouter un client"})

# Modification
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Informations client mises à jour.")
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form, 'title': "Modifier le client"})

# Détails (affiche aussi l'historique de ses devis)
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)

    # Récupération des devis du client
    devis_client = client.devis.all().order_by('-date_creation')  # Les plus récents en premier

    # Calcul des statistiques
    stats = {
        'total_devis': devis_client.count(),
        'montant_total_devis': devis_client.aggregate(
            total=Sum('total_ht')
        )['total'] or 0,
        
        'devis_acceptes': devis_client.count(),
        
        'total_maintenances': Maintenance.objects.filter(
            client=client
        ).count(),
    }

    # Calcul du taux de fidélité (optionnel mais recommandé)
    if stats['total_devis'] > 0:
        stats['taux_fidelite'] = round(
            (stats['devis_acceptes'] / stats['total_devis']) * 100, 1
        )
    else:
        stats['taux_fidelite'] = 0

    context = {
        'client': client,
        'devis': devis_client,           # ← Correspond au template que je t'ai donné
        'stats': stats,
    }

    return render(request, 'clients/client_detail.html', context)
# Suppression
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.warning(request, "Le client a été supprimé.")
        return redirect('client_list')
    return render(request, 'clients/client_confirm_delete.html', {'client': client})




def liste_tous_les_rapports(request):
    """Vue pour la section 'Rapports' de la sidebar (vue globale)"""
    query = request.GET.get('q')
    rapports = Rapport.objects.select_related('client').all()

    # Optionnel : Ajouter une barre de recherche par nom de rapport ou nom de client
    if query:
        rapports = rapports.filter(
            Q(nom__icontains=query) | 
            Q(client__nom__icontains=query)
        )

    return render(request, 'rapports/liste_rapports.html', {
        'rapports': rapports,
        'query': query
    })



def liste_rapports_client(request, client_id):
    """Affiche tous les rapports d'un client spécifique"""
    client = get_object_or_404(Client, id=client_id)
    rapports = client.rapports.all()
    return render(request, 'clients/client_detail.html', {
        'client': client,
        'rapports': rapports
    })

def ajouter_rapport(request, client_id=None):
    """Ajoute un rapport (lié à un client si client_id est fourni)"""
    client = None
    if client_id:
        client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        form = RapportForm(request.POST, request.FILES)
        if form.is_valid():
            rapport = form.save()
            messages.success(request, f"Le rapport '{rapport.nom}' a été ajouté avec succès.")
            return redirect('client_detail', pk=rapport.client.pk)
    else:
        # Si on arrive depuis la fiche client, on pré-sélectionne le client
        initial_data = {'client': client} if client else {}
        form = RapportForm(initial=initial_data)
    
    return render(request, 'rapports/formulaire.html', {
        'form': form,
        'client': client
    })

def supprimer_rapport(request, rapport_id):
    rapport = get_object_or_404(Rapport, id=rapport_id)
    client_pk = rapport.client.pk  # On garde le PK du client
    
    if request.method == 'POST':
        # Récupérer l'URL de la page précédente
        referer = request.META.get('HTTP_REFERER', '')
        
        # Suppression
        if rapport.fichier:
            rapport.fichier.delete()
        rapport.delete()
        
        messages.success(request, "Rapport supprimé avec succès.")

        # CONDITION DE REDIRECTION
        # Si l'URL de provenance contient 'clients/', on retourne à la fiche client
        if 'clients/' in referer:
            return redirect('client_detail', pk=rapport.client.pk)
        
        # Sinon, on retourne à la liste générale des rapports
        return redirect('liste_tous_les_rapports')

    return redirect('liste_tous_les_rapports')
def modifier_rapport(request, rapport_id):
    """Modifie un rapport existant"""
    rapport = get_object_or_404(Rapport, id=rapport_id)
    client = rapport.client # Pour garder le contexte du client
    
    if request.method == 'POST':
        # On passe l'instance pour mettre à jour l'objet existant au lieu d'en créer un nouveau
        form = RapportForm(request.POST, request.FILES, instance=rapport)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le rapport '{rapport.nom}' a été mis à jour.")
            return redirect('client_detail', pk=rapport.client.pk)
    else:
        form = RapportForm(instance=rapport)
    
    return render(request, 'rapports/formulaire.html', {
        'form': form,
        'rapport': rapport,
        'client': client,
        'en_edition': True # Petit flag pour changer le titre dans le HTML
    })