from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone



class Client(models.Model):
    nom = models.CharField(_("Nom complet"), max_length=255)
    email = models.EmailField(_("Adresse email"), unique=True)
    telephone = models.CharField(_("Téléphone"), max_length=20)
    adresse = models.TextField(_("Adresse"), blank=True)
    date_creation = models.DateTimeField(_("Date de création"), auto_now_add=True)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom

    @property
    def total_devis(self):
        # On utilise le count() sur le set lié (devis_set)
        return self.devis.count()

    # @property
    # def total_maintenances(self):
    #     return self.maintenance.count()

    
class Devis(models.Model):
    STATUTS = [
        ('envoye', _('Envoyé')),
        ('accepte', _('Accepté')),
        ('refuse', _('Refusé')),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devis')
    reference = models.CharField(_("Référence"), max_length=50, unique=True, editable=False)
    objet = models.CharField(_("Objet"), max_length=255)
    date_creation = models.DateField(auto_now_add=True)
    date_validite = models.DateField(_("Date de validité"))
    statut = models.CharField(max_length=20, choices=STATUTS, default='envoye')
    total_ht = models.DecimalField(max_digits=15, decimal_places=0, default=0)

    class Meta:
        verbose_name = _("Devis")
        ordering = ['-date_creation']
    def save(self, *args, **kwargs):
        if not self.reference:
            annee = timezone.now().year
            # On récupère le dernier devis de l'année en cours
            dernier_devis = Devis.objects.filter(
                reference__startswith=f"DEV-{annee}-"
            ).order_by('-reference').first()

            if dernier_devis:
                # On extrait le numéro de "DEV-2026-0005" -> 5
                try:
                    dernier_numero = int(dernier_devis.reference.split('-')[-1])
                    nouveau_numero = dernier_numero + 1
                except (ValueError, IndexError):
                    nouveau_numero = 1
            else:
                nouveau_numero = 1
            
            self.reference = f"DEV-{annee}-{nouveau_numero:04d}"
            
        super().save(*args, **kwargs)
    
    def update_total(self):
        # Utilise l'agrégation de base de données pour être plus rapide
        from django.db.models import Sum
        # On calcule le montant de toutes les lignes liées aux sections de ce devis
        total = LigneDevis.objects.filter(section__devis=self).aggregate(
            total=models.Sum(models.F('prix_unitaire') * models.F('quantite'))
        )['total'] or 0
        
        self.total_ht = total
        self.save(update_fields=['total_ht'])

    def __str__(self):
        return self.reference

class SectionDevis(models.Model):
    """Ex: Étude hydrogéologique, Forage, Pompe submersible..."""
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='sections')
    titre = models.CharField(_("Titre de la section"), max_length=255)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']
        verbose_name = _("Section de devis")

    @property
    def total_section(self):
        return sum(ligne.montant_ligne for ligne in self.lignes.all())

    def __str__(self):
        return f"{self.titre} ({self.devis.reference})"

class LigneDevis(models.Model):
    section = models.ForeignKey(SectionDevis, on_delete=models.CASCADE, related_name='lignes')
    designation = models.CharField(_("Désignation"), max_length=255)
    unite = models.CharField(_("Unité"), max_length=20, default="ff")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    @property
    def montant_ligne(self):
        """Calcul automatique : PU * Qté"""
        return int(self.prix_unitaire * self.quantite)

    class Meta:
        verbose_name = _("Ligne de devis")



