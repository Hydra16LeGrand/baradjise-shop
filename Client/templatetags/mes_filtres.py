from django import template
from Client import models
from datetime import date
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

register = template.Library()

@register.filter(name='multiplication')
def multiplication(a, b):
	return a*b


@register.filter()
def division(a, b):
	return a/b

@register.filter()
def soustraction(a, b,c):

	return b-a-c


@register.filter(name='filtre')
def filtre(model, parametre):

	resultat = model.filter(parametre=parametre)
	return resultat

@register.filter()
def filtre_historique_paiement_vendeur(cmd, produit):

	panier_produit =[]
	for pp in cmd.panierproduit_set.filter(produit=produit):
		panier_produit.append(pp)

	return panier_produit
	
@register.filter()
def affectation(a, b):
	b=a

@register.filter()
def prix_quantite(prix, quantite):

	return prix, quantite

@register.filter()
def calcul_montant(prix_quantite, commission):

	prix, quantite = prix_quantite

	return prix*quantite*(1-commission/100)


@register.simple_tag()
def calcul_montant_2(prix, quantite, commission):

	return prix*quantite*(1-commission/100)


@register.filter()
def differentes_commandes(historiques):

	num_cmd = []
	differentes_commandes =[]
	for historique in historiques:

		if not historique.num_cmd in num_cmd:
			num_cmd.append(historique.num_cmd)
			differentes_commandes.append(historique)

	return differentes_commandes


@register.filter()
def taille(liste):

	return len(liste)


@register.filter()
def conversion_date_jour(date):

	la_date = date.today() - date
	return la_date.days

@register.filter()
def sous_total(panier_produit):

	sous_total = 0
	for pp in panier_produit:
		sous_total += pp.quantite * pp.produit.prix

	return sous_total

@register.filter()
def retourner_client(username, colonne):

	user = User.objects.get(username=username)
	client =  models.User.objects.get(user= user)
	if colonne == 'email':
		return client.user.email
	elif colonne == 'contact1':
		return client.contact1
	elif colonne == 'ville':
		return client.ville	
	elif colonne == 'commune':
		return client.commune
	elif colonne == 'quartier':
		return client.quartier

@register.filter()
def reccup_produit_cmd(num_cmd):

	historiques = models.Historique.objects.filter(num_cmd=num_cmd)
	return historiques

@register.simple_tag()
def reccup_image_produit_cmd(libelle, categorie, prix_vendeur, prix):

	try:
		produit = models.Produit.objects.get(libelle=libelle, categorie=categorie, prix_vendeur=prix_vendeur, prix=prix)
	except:
		return "/media/image_produit/pas_d_image.jpg"
	else:
		return produit.get_image


@register.filter()
def verif_existance_livreur(livreur):

	if livreur:
		return True
	else:
		return False

@register.filter()
def promo(temp):
	promo = date(2021, 3, 31) - date.today()
	return promo.days


@register.filter()
def parse_int(prix):

	return int(prix)

@register.filter()
def nbre_pp(requete):

	try:
		user = models.User.objects.get(user = User.objects.get(username=requete.user))
		panier = models.Panier.objects.get(user=user)
	except Exception as e:
		return redirect('deconnexion')
	else:
		nbre_pp = 0
		for pp in models.PanierProduit.objects.filter(panier=panier).exclude(status=1):
			nbre_pp += 1

		return nbre_pp		


@register.filter()
def nbre_pu(requete):

	try:
		user = models.User.objects.get(user = User.objects.get(username=requete.user))
	except Exception as e:
		return redirect('deconnexion')
	else:
		nbre_pu = 0
		for pp in models.ProduitUser.objects.filter(user=user):
			nbre_pu += 1

		return nbre_pu