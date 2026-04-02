from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from weasyprint import HTML
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory
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
    """Génération PDF A4 avec Header (P1) et Footer (Fin)"""
    devis = get_object_or_404(Devis, pk=pk)
    entreprise = Entreprise.objects.first()
    logo_path = finders.find('logo.png')
    
    html_string = render_to_string('devis/pdf_template.html', {
        'devis': devis,
        'entreprise': entreprise,
        'sections': devis.sections.all(),
        'logo_path': logo_path, 
    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Devis_{devis.reference}.pdf"'
    return response



from django.db.models import Q
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