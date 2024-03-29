from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Produit)
class ProduitAdmin(admin.ModelAdmin):
	list_display = ("libelle", "prix_vendeur", "prix", "quantite", "status", "image", "vendeur")
	empty_value_display = '-empty-'

@admin.register(models.Commande)
class CommandeAdmin(admin.ModelAdmin):
	list_display = ("panier", "date", "status", "montant")

@admin.register(models.Livraison)
class LivraisonAdmin(admin.ModelAdmin):
	list_display = ("commande", "livreur", "adresse_livraison", "frais", "date_livraison", "status")

@admin.register(models.Livreur)
class LivreurAdmin(admin.ModelAdmin):
	list_display = ("nom", "prenom", "cin", "contact", "existance")

@admin.register(models.Paiement)
class PaiementAdmin(admin.ModelAdmin):
	list_display = ("commande", "moyen_paiement", "montant_total", "status")

@admin.register(models.PanierProduit)
class PanierProduitAdmin(admin.ModelAdmin):
	list_display = ("panier", "produit", "commande", "quantite", "date_ajout", "date_modification", "status")

# @admin.register(models.Panier)
# class Panier(admin.ModelAdmin):
# 	list_display = ("user", "produit")

@admin.register(models.ProduitUser)
class ProduitUser(admin.ModelAdmin):
	list_display = ("produit", "user")

# @admin.register(models.User)
# class User(admin.ModelAdmin):
# 	list_display = ("contact1", "ville", "commune", "quartier", "profil", "produit", "user")

@admin.register(models.Vendeur)
class Vendeur(admin.ModelAdmin):
	list_display = ("contact1", "ville", "commune", "quartier", "user")

@admin.register(models.Historique)
class Historique(admin.ModelAdmin):
	list_display = ("num_cmd","date_cmd","montant_cmd","libelle", "prix_vendeur", "prix", "quantite", "frais_livraison", "adresse_livraison",
		"status_livraison","livreur", "moyen_paiement", "montant_total", "status_paiement", "date_paiement", "client", "vendeur")
	empty_value_display = '-vide-'
	list_display_links = ("num_cmd", "montant_cmd")
	list_editable = ("status_paiement", "status_livraison", "livreur")


admin.site.register(models.User)
admin.site.register(models.ImageProduit)
admin.site.register(models.Avis)
