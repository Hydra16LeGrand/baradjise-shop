from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import  date
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
import random
import os, json, boto3
# import pyrebase

from . import models

# Create your views here.

# Les Configurations Firebase pour l'authentification et l'inscription des clients
# firebaseConfig = {
#     "apiKey": "AIzaSyAcIgIdfW6JQOwi7fVjsPV54ouOVfBQgdI",
#     "authDomain": "projet-commerce.firebaseapp.com",
#     "databaseURL": "https://projet-commerce.firebaseio.com",
#     "projectId": "projet-commerce",
#     "storageBucket": "projet-commerce.appspot.com",
#     "messagingSenderId": "647035456259",
#     "appId": "1:647035456259:web:2c61b586513be282fff736",
#     "measurementId": "G-4XKQVRYXT9"
#     }
# firebase = pyrebase.initialize_app(firebaseConfig)
# firebase_auth = firebase.auth()
# database = firebase.database()


# Classe permettant de gerer le systeme d'authentification du client
class Acces:

	def inscription(request):

		if request.method == "POST":
			form = request.POST

			if form.get('mdp') == form.get('c_mdp'):

				if len(form.get('mdp')) >= 6:

					if len(form.get('contact1')) == 10:

						try:
							user = User.objects.get(username=form.get('username'))
						except Exception as e:

							try:
								user = User.objects.create_user(
									username=form.get('username'), 
									password=form.get('mdp'),
									email=form.get('email'),
									last_name=form.get('nom'),
									first_name=form.get('prenom'),
									is_active=True)

							except Exception as e:
								return render(request, "Client/authentification.html", {
								'message': "Erreur lors de la création du compte.\nSi cela persiste Veuillez contacter le service client au 0556748529"
								})
							else:
								try:
									client = models.User.objects.create(
										contact1 = form.get('contact1'),
										contact2 = form.get('contact2'),
										ville = form.get('ville'),
										commune = form.get('commune'),
										quartier = form.get('quartier'),
										user = user)
								except Exception as e:
									user.delete()
									return render(request, "Client/authentification.html", {
								'message': "Erreur lors de la création du compte.\nSi cela persiste Veuillez contacter le service client au 0556748529"
								})
								else:
									models.Panier.objects.create(user=client)
									return render(request, "Client/authentification.html", {'message': "Votre compte a été creer avec succès"})
						else:
							return render(request, "Client/inscription.html", {
								'message': "Un compte est deja associe a ce nom d'utilisateur ou cet email", 'form': form})
					else:
						return render(request, "Client/inscription.html", {'message': "Votre numeros de telephone doit etre egale a 8 chiffres", 'form': form})
				else:
					return render(request, "Client/inscription.html", {'message': "Le mot de passe doit contenir au moins 6 caracteres", 'form': form})
			else:
				return render(request, "Client/inscription.html", {'message': "Les mots de passe saisis ne correspondent pas", 'form': form})
		else:
			return render(request, "Client/inscription.html")

	def authentification(request):

		if request.method == 'POST':

			form = request.POST
			# authenticate renvoi None si le auth_user n'existe pas et le champ de auth_user sinon
			try:
				client = models.User.objects.get(user=User.objects.get(username=form.get('username')))
			except:
				return render(request, "Client/authentification.html", {'message':"Compte inexistant"})
			else:
				user = authenticate(username=form.get('username'), password=form.get('mdp'))
				if user is not None:
					login(request, user)
					return redirect('accueil')
				else:
					return render(request, "Client/authentification.html", {'message': "E-mail ou mot de passe incorrect"})

		else:
			return render(request, "Client/authentification.html")

	def deconnexion(request):

		logout(request)
		return redirect('accueil')

class Panier:

	def ajouter(request, id_produit):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				try:
					panier = models.Panier.objects.get(user=client)
					produit = models.Produit.objects.get(id=id_produit)
				except Exception as e:
					return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
				else:
					# On tente de reccuperer le produit lie au panier. Histoire de voir s'il na pas encore ete ajoute
					try:
						panier_produit = models.PanierProduit.objects.get(produit=produit, panier=panier, status=0)
					except Exception as e:
						# Si le produit nest pas dans le panier on l'ajoute
						try:
							models.PanierProduit.objects.create(produit = produit, panier = panier)
						except Exception as e:
							return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
						else:
							return redirect('lister_panier')
					else:
						return redirect('lister_panier')

	def lister(request):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				try:
					panier = models.Panier.objects.get(user=client)
					# Liste des produits dont on a pas confirmer la commande
					panier_produit = models.PanierProduit.objects.filter(panier=panier, status=0)
					gain = 0.0
					for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
						gain += pp.quantite*(pp.produit.prix-pp.produit.prix_vendeur)
				except Exception as e:
					return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
				else:
					return render(request, "lister_panier.html",{'panier': panier, 'panier_produit': panier_produit, 'gain': gain, 'active':"panier"})

	# Suppression du produit du panier
	def supprimer(request, id_produit):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				try:
					panier = models.Panier.objects.get(user=client)
					produit = models.Produit.objects.get(id=id_produit)
					produit_a_supprimer = models.PanierProduit.objects.get(panier=panier, produit=produit, status=0)
				except Exception as e:
					return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
				else:
					produit_a_supprimer.delete()
					return redirect('lister_panier')

	# changer la quantite d'un produit dans le panier
	def modifier(request, id_produit):

		if not request.user.is_authenticated:
			return redirect('authentification')
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			try:
				form = request.POST
				panier = models.Panier.objects.get(user=client)
				produit = models.Produit.objects.get(id=id_produit)

				# On verifie si la quantite saisie n'est pas superieure a la quantite du produit
				# Cela a ete fais egalement dans le template
				if produit.quantite >= int(form.get('quantite')):
					panier_produit = models.PanierProduit.objects.get(panier=panier, produit = produit, status=0)
					panier_produit.quantite = form.get('quantite')
				panier_produit.save()
			except Exception as e:
				return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
			else:
				return redirect('lister_panier')

	def finaliser_commande(request):

		if not request.user.is_authenticated:
			return redirect('authentification')
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect("authentification")
			else:
				# Calcul du montant de la commande
				try:
					panier = models.Panier.objects.get(user=client)
					montant=0.0
					for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
						montant += pp.quantite*pp.produit.prix

				except Exception as e:
					return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
				else:
					# Creation de la commande

					try:
						commande = models.Commande.objects.create(
							panier = panier,
							montant=montant)

						for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
							# if not pp.commande:
							pp.commande = commande
							
							pp.produit.quantite -= pp.quantite
							pp.produit.save()
							pp.save()

					except Exception as e:
						return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
					else:
						# Creation de la livraison
						try:
							adresse_livraison = request.POST.get('adresse_livraison')
							if adresse_livraison == "abidjan":
								promo = date(2021, 3, 31) - date.today()

								if promo.days >= 0:
									livraison = models.Livraison.objects.create(
										commande=commande,
										adresse_livraison = adresse_livraison,
										frais=0.0,
										date_livraison = date(year=date.today().year, month=date.today().month, day=date.today().day+1),
										status = 'en_cours'
										)
								else:
									livraison = models.Livraison.objects.create(
										commande=commande,
										adresse_livraison = adresse_livraison,
										frais=1500.0,
										date_livraison = date(year=date.today().year, month=date.today().month, day=date.today().day+1),
										status = 'en_cours'
										)
							else:
								livraison = models.Livraison.objects.create(
									commande=commande,
									adresse_livraison = adresse_livraison,
									frais=3000.0,
									date_livraison = date(year=date.today().year, month=date.today().month, day=date.today().day+2),
									status = 'en_cours'
									)
						except Exception as e:
							return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
						else:
							# Creation du paiement
							try:
								montant_total = montant+livraison.frais
								paiement = models.Paiement.objects.create(
									commande=commande,
									montant_total=montant_total,
									status='en_cours')
							except Exception as e:
								return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
							else:
								try:

									for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
										models.Historique.objects.create(

											num_cmd = commande.pk,
											montant_cmd = montant,

											libelle = pp.produit.libelle,
											categorie = pp.produit.categorie.nom,
											prix_vendeur = pp.produit.prix_vendeur,
											prix = pp.produit.prix,
											quantite = pp.quantite,

											frais_livraison = livraison.frais,
											adresse_livraison = livraison.adresse_livraison,

											moyen_paiement = paiement.moyen_paiement,
											montant_total = paiement.montant_total,

											client = client.user.username,
											vendeur = pp.produit.vendeur.user.username,
											)
										pp.status=1
										pp.save()
								except Exception as e:
									# paiement.delete()
									# livraison.delete()
									commande.delete()
									return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
								else:
									return redirect('mes_commandes')

		
#Gestion de la recherche 

class Recherche:

	# Les autres methodes de recherches seront redirigees ici
	def recherche(request, vue, requete):

		# On teste si la requete viens de tous_les_produits
		if requete == " ":
			produits = models.Produit.objects.filter(status=1).exclude(quantite=0)
			# On verifie si un formulaire de prix est transmis
			if request.method == 'POST':
				form = request.POST
				# Si un prix minimum et maximum sont saisis:
				if not form.get('prix_min') == '' and not form.get('prix_max') =='':
					produits = produits.filter(Q(prix__range(form.get('prix_min'), form.get('prix_max'))))
				elif not form.get('prix_max')=='' and form.get('prix_min')=='':
					produits = produits.filter(prix__lte=form.get('prix_max'))
				elif not form.get('prix_min')=='' and form.get('prix_max')=='':
					produits = produits.filter(prix__gte=form.get('prix_min'))

		else:
			# On teste si la requete viens de la methode rechercher_categorie
			try:
				categorie = models.Categorie.objects.get(nom=requete)
			except Exception as e:
				# On cherche a savoir si le formulaire de prix a ete transmis
				if request.method == 'POST':
					form = request.POST
					# Si ce n'est pas le cas, on teste si la requete viens de la methode rechercher_boutique
					try:
						user = User.objects.get(username=requete)
						vendeur = models.Vendeur.objects.get(user=user)
					except Exception as e:
						# Sinon la recherche viens de barre_recherche
						# On fais des verifications sur les prix egalement
						if not form.get('prix_min') == '' and not form.get('prix_max') =='':
							produits = models.Produit.objects.filter(
								Q(libelle__icontains=requete)|
								Q(description__icontains=requete)&
								Q(prix__range=(form.get('prix_min'), form.get('prix_max')))).exclude(quantite=0)
						elif not form.get('prix_max')=='' and form.get('prix_min')=='':
							produits = models.Produit.objects.filter(
								(Q(libelle__icontains=requete)|
								Q(description__icontains=requete))&
								Q(prix__lte=form.get('prix_max'))&
								Q(status=1))
						elif not form.get('prix_min')=='' and form.get('prix_max')=='':
							produits = models.Produit.objects.filter(
								(Q(libelle__icontains=requete)|
								Q(description__icontains=requete))&
								Q(prix__gte=form.get('prix_min'))&
								Q(status=1))
						else:
							produits = models.Produit.objects.filter(
								(Q(libelle__icontains=requete)|
								Q(description__icontains=requete))&
								Q(status=1))
					else:
						produits = models.Produit.objects.filter(vendeur=vendeur).exclude(quantite=0)
						if not form.get('prix_min') == '' and not form.get('prix_max') =='':
							produits = produits.filter(Q(prix__range(form.get('prix_min'), form.get('prix_max'))))
						elif not form.get('prix_max')=='' and form.get('prix_min')=='':
							produits = produits.filter(prix__lte=form.get('prix_max'))
						elif not form.get('prix_min')=='' and form.get('prix_max')=='':
							produits = produits.filter(prix__gte=form.get('prix_min'))
				# Si le formulaire na pas ete transmis, on ne fais pas de verifications sur les prix
				else:
					try:
						user = User.objects.get(username=requete)
						vendeur = models.Vendeur.objects.get(user=user)
					except Exception as e:
						produits = models.Produit.objects.filter(
							Q(libelle__icontains=requete)|
							Q(description__icontains=requete)).exclude(quantite=0)
					else:
						produits = models.Produit.objects.filter(vendeur=vendeur).exclude(quantite=0)

			# Si la requete viens belle et bien de rechercher_categorie
			else:
				# On verifie si un formulaire de prix est transmis
				if request.method == 'POST':
					form = request.POST
					# Si un prix minimum et maximum sont saisis:
					if not form.get('prix_min') == '' and not form.get('prix_max') =='':
						# On reccupere les produits avec les conditions ci dessous
						produits = models.Produit.objects.filter(

							(Q(libelle__icontains=requete)|
							Q(categorie=categorie)|
							Q(description__icontains=requete))&
							Q(prix__range=(form.get('prix_min'), form.get('prix_max')))&
							Q(status=1))

					elif not form.get('prix_max')=='' and form.get('prix_min')=='':
						produits = models.Produit.objects.filter(

							(Q(libelle__icontains=requete)|
							Q(categorie=categorie)|
							Q(description__icontains=requete))&
							Q(prix__lte=form.get('prix_max'))&
							Q(status=1))

					elif not form.get('prix_min')=='' and form.get('prix_max')=='':
						produits = models.Produit.objects.filter(

							(Q(libelle__icontains=requete)|
							Q(categorie=categorie)|
							Q(description__icontains=requete))&
							Q(prix__gte=form.get('prix_min'))&
							Q(status=1))

					else:
						produits = models.Produit.objects.filter(
							(Q(libelle__icontains=requete)|
								Q(categorie=categorie)|
								Q(description__icontains=requete))&
							Q(status=1))
					produits = produits.exclude(quantite=0)
				# Sinon on ne fais pas de verifications sur les prix
				else:
					produits = models.Produit.objects.filter(
						Q(libelle__icontains=requete)|
						Q(libelle__icontains=categorie.nom)|
						Q(categorie=categorie)|
						Q(description__icontains=requete)).exclude(quantite=0)

		# Preparation du rendu de la vue
		produits = list(produits)
		produits = random.sample(produits, len(produits))

		paginator = Paginator(produits, 12)
		nombre_page = request.GET.get('page')
		page_obj = paginator.get_page(nombre_page)

		if vue=="list":
			return render(request, "resultat_recherche.html", {'produits':page_obj, 'requete': requete, 'vue':vue, 'nbre_produits':len(produits)})
		else:
			return render(request, "resultat_recherche_grid.html", {'produits':page_obj, 'requete': requete, 'vue':vue, 'nbre_produits':len(produits)})

	# Methode a utilise pour la barre de recherche
	def barre_recherche(request):

		if request.method == 'POST':
			form = request.POST
			produits = models.Produit.objects.filter(
				Q(libelle__icontains=form.get('requete'))|
				Q(description__icontains=form.get('requete'))&
				Q(status=1)
				).exclude(quantite=0)

			return redirect('rechercher_produit', 'list', form.get('requete'))
		else:
			return redirect('accueil')

	# methode de recherche de categorie
	def rechercher_categorie(request, categorie):

		try:
			categorie = models.Categorie.objects.get(cle=categorie)
		except Exception as e:
			return redirect('rechercher_produit', 'grid', categorie)
		else:
			return redirect('rechercher_produit', 'grid', categorie.nom)

	# Methode permettant de rendre la boutique du vendeur
	def rechercher_boutique(request, vendeur):

		try:
			user = User.objects.get(username=vendeur)
		except Exception as e:
			return HttpResponse("boutique introuvable")
		else:
			logout(request)
			return redirect('rechercher_produit', 'list', user.username)

	# methode de renvois de tous les produits
	def tous_les_produits(request):

		return redirect('rechercher_produit', 'list', " ")

def dashboard_client(request):

	if not request.user.is_authenticated:
			return redirect("authentification")
	else:
		try:
			user = User.objects.get(username=request.user)
			client = models.User.objects.get(user=request.user)
		except Exception as e:
			return redirect("authentification")
		else:
			try:
				panier = models.Panier.objects.get(user=client)
				nbre_cmd = 0
				att_livr = 0
				livree = 0
				nbre_produit_panier = 0

				num_cmd = []
				for his in models.Historique.objects.filter(client=user.username):
					if not his.num_cmd in num_cmd:
						nbre_cmd+=1
						num_cmd.append(his.num_cmd)
					if his.status_livraison == 'en_cours':
						att_livr +=1
					if his.status_livraison == 'faite':
						livree +=1

				for pp in models.PanierProduit.objects.filter(panier=panier, status=0):
					nbre_produit_panier += 1

				nbre_souhait = 0
				for souhait in client.produituser_set.all():
					nbre_souhait+=1

			except Exception as e:
				return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
			else:
				return render(request, "Client/dashboard.html", {
					'client': client, 
					'nbre_cmd': nbre_cmd, 
					'nbre_souhait':nbre_souhait, 
					'att_livr': att_livr, 
					'livree': livree, 
					'nbre_produit_panier':nbre_produit_panier,
					'active':"dashboard"})


# Page d'accueil
def accueil(request):

	try:
		produits = models.Produit.objects.filter(status=1).exclude(quantite=0)
		produits = list(produits)

		produits = random.sample(produits, len(produits))
		i=0
		produits_temp = []
		for produit in produits:
			if i == 20:
				break
			else:
				produits_temp.append(produits[i])
				i+=1
		# paginator = Paginator(produits, 20)

		# nombre_page = request.GET.get('page')
		# page_obj = paginator.get_page(nombre_page)



	except Exception as e:
		return HttpResponse("Erreur, Si le problème persiste veuillez contacter le service client au 0556748529")
	else:
		return render(request, "accueil.html", {'produits':produits_temp, 'requete': ""})

# Commandes passees par les clients
def mes_commandes(request):

	if not request.user.is_authenticated:
		return redirect("authentification")
	else:
		try:
			client = models.User.objects.get(user=request.user)
		except Exception as e:
			return redirect("authentification")
		else:
			try:
				historiques = models.Historique.objects.filter(client=request.user).order_by("-date_cmd")
			except Exception as e:
				return HttpResponse("Erreur, Si le problème persiste, veuillez contacter le service client au 0556748529")
			else:
				return render(request, "Client/mes_commandes.html", {
							'historiques': historiques, 'active':"commande"})

# Detail du produit
def detail_produit(request, id_produit):

	try:
		produit = models.Produit.objects.get(pk=id_produit)
	except Exception as e:
		return HttpResponse("Produit introuvable")
	else:
		return render(request, "Client/detail_produit.html", {'produit':produit})

class Envie:

	def ajouter(request, id_produit):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				produit = models.Produit.objects.get(pk=id_produit, status=1)
			except Exception as e:
				return HttpResponse("Produit introuvable")
			else:
				try:
					client = models.User.objects.get(user=request.user)
				except Exception as e:
					return redirect('authentification')
				else:
					try:
						produit_user =  models.ProduitUser.objects.get(produit=produit, user=client)
					except Exception as e:
						produit_user = models.ProduitUser.objects.create(produit=produit, user=client)
						return redirect('lister_envie')
					else:
						return redirect('accueil')

	def lister(request):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return HttpResponse("Erreur, Si le problème persiste, veuillez contacter le service client au 0556748529")
			else:
				try:
					produit_user = models.ProduitUser.objects.filter(user=client)
				except Exception as e:
					return HttpResponse("Erreur, Si le problème persiste, veuillez contacter le service client au 0556748529")
				else:
					return render(request, "Client/mes_envies.html", {'produit_user':produit_user, 'active':"souhait"})

	def supprimer(request, id_produit_user):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return HttpResponse("Erreur, Si le problème persiste, veuillez contacter le service client au 0556748529")
			else:
				try:
					produit_user = models.ProduitUser.objects.get(pk=id_produit_user)
				except Exception as e:
					return HttpResponse("Erreur, si le problème persiste, veuillez nous contacter au 0556748529")
				else:
					produit_user.delete()
					return redirect('lister_envie')

class Compte:

	# Changer les informations sur un utilisateur
	def changer_infos_user(request):

		if not request.user.is_authenticated:
			return redirect("authentification")
		else:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return HttpResponse("Erreur, Si le problème persiste veuillez contacter le service client au 0556748529")
			else:
				if request.method == 'POST':
					form = request.POST
					if len(form.get('contact1')) == 10:

						try:
							client.user.email = form.get('email')
							client.contact1 = form.get('contact1')
							client.contact2 = form.get('contact2')
							client.ville = form.get('ville')
							client.commune = form.get('commune')
							client.quartier = form.get('quartier')
							client.user.save()
							client.save()
						except Exception as e:
							return HttpResponse("Erreur, Si le problème persiste veuillez contacter le service client au 0556748529")
						else:
							if form.get('mdp') and form.get('c_mdp'):
								if form.get('mdp') == form.get('c_mdp'):
									if len(form.get('mdp')) >= 6:
										client.user.set_password(form.get('mdp'))
										return render(request, "Client/changer_infos_user.html",{'user':client,
											'message': "Les infos ont ete mis a jour", 'active':"parametre"
											})
									else:
										return render(request, "Client/changer_infos_user.html", {'user':client,
	'message': "Les modifications ont ete apportees Cependant, le mot de passe reste inchange car mot de passe doit etre superieur ou egale a 6 caracteres"})
								else:
									return render(request, "Client/changer_infos_user.html", {'user':client,
			'message': "Les modifications ont ete apportees Cependant, le mot de passe reste inchange car les mots de passe saisis ne correspondent pas."})
							else:
								return render(request, "Client/changer_infos_user.html", {'user':client, 'message': "Les infos ont ete mis a jour"})

					else:
						return render(request, "Client/changer_infos_user.html", {'user':client,
							'message': "Veuillez saisir des numeros de telephone correct"})

				else:
					return render(request, "Client/changer_infos_user.html", {'user':client, 'active': "parametre"})

	def changer_profil_user(request):

		if request.user.is_authenticated:
			try:
				client = models.User.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification')
			else:
				if request.method == 'POST':

					form_profil = request.FILES
					try:
						client.profil = form_profil.get('profil')
						client.save()
					except Exception as e:
						return HttpResponse("Erreur, Si le problème persiste veuillez contacter le service client au 0556748529")
					else:
						return render(request, "Client/changer_infos_user.html", {
							'user': client, 'message': "Votre profil a ete mis a jour",
							'active':"parametre"})
				else:
					return render(request, "Client/changer_infos_user.html", {
						'user': client,
						'active': "parametre"})
		else:
			return redirect('authentification')
# Gestion des vendeurs
class Vendeur:

	# Le systeme d'authentification ne se fait pas avec Firebase mais avec celui de django

	def inscription(request):

		if request.method == 'POST':

			form = request.POST

			if form.get('mdp') == form.get('c_mdp'):

				if len(form.get('mdp'))>=6:

					if len(form.get('contact1')) == 10 and len(form.get('contact2')) == 10:
						# Tentative de reccuperation du vendeur dans la table auth_user. Pour voir s'il n'est pas encore enregistre
						try:
							# Gag, je venais de decouvrir la classe Q, il fallait la tester.
							user = User.objects.get(Q(username=form.get('username')) | Q(email=form.get('email')))
						except Exception as e:
							# S'il ne l'est pas on l'enregistre dans auth_user
							try:
								user = User.objects.create_user(
									username=form.get('username'), 
									password=form.get('mdp'),
									email=form.get('email'),
									last_name=form.get('nom'),
									first_name=form.get('prenom'),
									is_active=False)
							except Exception as e:
								return render(request, "Vendeur/inscription.html", {
									'message': "Erreur lors de la création du compte. Si le problème persiste, veuillez nous contacter au 0556748529"
									})
							else:
								# On cree le vendeur associe
								try:
									vendeur = models.Vendeur.objects.create(
										contact1 = form.get('contact1'),
										contact2 = form.get('contact2'),
										ville = form.get('ville'),
										commune = form.get('commune'),
										quartier = form.get('quartier'),
										user = user)
								except Exception as e:
									user.delete()
									return render(request, "Vendeur/inscription.html", {
									'message': "Erreur lors de la création du compte. Si le problème persiste, veuillez nous contacter au 0556748529"
									})
								else:
									return render(request, "Vendeur/authentification.html", {
										'message': "Votre compte a ete enregistrer. Vous serez contacte pour la confirmation"})
						else:
							return redirect('authentification_vendeur')

					else:
						return render(request, "Vendeur/inscription.html", {'message': "Veuillez saisir des numeros de telephone a 10 chiffres"})
				else:
					return render(request, "Vendeur/inscription.html", {'message': "Le mot de passe doit etre superieur a 10 caracteres"})

			else:
				return render(request, "Vendeur/inscription.html", {'message': "Les mots de passe saisies ne correspondent pas"})
		else:
			return render(request, "Vendeur/inscription.html")

	def authentification(request):

		if request.method == 'POST':

			form = request.POST
			# authenticate renvoi None si le auth_user n'existe pas et le champ de auth_user sinon
			try:
				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=form.get('username')))
			except Exception as e:
				return render(request, "Vendeur/authentification.html", {'message': "Compte inexistant"})
			else:
				user = authenticate(username=form.get('username'), password=form.get('mdp'))
				if user is not None:
					login(request, user)
					return redirect('dashboard_vendeur')
				else:
					if user.is_active:
						return render(request, "Vendeur/authentification.html", {'message': "E-mail ou mot de passe incorrect"})
					else:
						return render(request, "Vendeur/authentification.html", {
							'message': "Votre compte n'a pas encore ete active. Veuillez nous contacter, si cela prend trop de temp"})

		else:
			return render(request, "Vendeur/authentification.html")

	# De parler? Tchrrr
	def deconnexion(request):

		logout(request)
		return redirect('authentification_vendeur')

	def dashboard(request):
		# Verification s'il est authentifie
		if request.user.is_authenticated:
			# On reccupere le vendeur et ses produits.
			try:
				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=request.user))
			except:
				return redirect('authentification_vendeur')
			else:

				try:
					nbre_produits = 0
					nbre_art_actif = 0
					nbre_art_vendu = 0

					for produit in models.Produit.objects.filter(vendeur=vendeur):
						nbre_produits += 1

						if produit.status == True:
							nbre_art_actif += 1

					for his in models.Historique.objects.filter(vendeur=vendeur.user.username):
						nbre_art_vendu += 1
				except Exception as e:
					return HttpResponse("Erreur, si le problème persiste veuillez nous contacter au 0556748529")
				else:
					return render(request, "Vendeur/dashboard.html", {
						'vendeur': vendeur,
						'nbre_produits': nbre_produits,
						'nbre_art_actif': nbre_art_actif,
						'nbre_art_vendu': nbre_art_vendu,
						'active': "dashboard_vendeur"})
		else:
			return redirect('authentification_vendeur')

	def liste_produit(request):

		if request.user.is_authenticated:
			# On reccupere le vendeur et ses produits.
			try:
				vendeur = models.Vendeur.objects.get(user=User.objects.get(username=request.user))
			except:
				return redirect('authentification_vendeur')
			else:

				if request.method == 'POST':
					produits =models.Produit.objects.filter(
						Q(vendeur=vendeur)&
						Q(libelle__icontains = request.POST.get('requete'))
						).order_by("date_ajout")
				else:
					produits = models.Produit.objects.filter(vendeur=vendeur).order_by("date_ajout")
					
				produits = list(produits)
				produits = random.sample(produits, len(produits))

				paginator = Paginator(produits, 12)
				nombre_page = request.GET.get('page')
				page_obj = paginator.get_page(nombre_page)
				return render(request, "Vendeur/liste_produits.html",{
					'produits': page_obj,
					'active': "liste_produits_vendeur",
					'nbre_produits': len(produits)
					})

		else:
			return redirect('authentification_vendeur')


	def ajouter_produit(request):

		if request.user.is_authenticated:

			if request.method == 'POST':

				form = request.POST
				form_image = request.FILES
				try:
					vendeur = models.Vendeur.objects.get(user=request.user)
				except Exception as e:
					return redirect('authentification_vendeur')
				else:
					try:
						categorie = models.Categorie.objects.get(cle=form.get('categorie'))
						prix = float(form.get('prix_vendeur'))*(1+ categorie.commission/100.0)
						produit = models.Produit.objects.create(
							libelle = form.get('libelle'),
							categorie = categorie,
							description = form.get('description'),
							prix_vendeur = form.get('prix_vendeur'),
							prix = prix,
							quantite =form.get('quantite'),
							moq = 1,
							status = True,
							image = form_image.get('image'),
							vendeur = vendeur,
							)	
					except Exception as e:
						return render(request, "Vendeur/ajouter_produit.html", {
							'message':"Erreur lors de l'ajout de produit. Si le problème persiste veuillez nous contacter au 0556748529"
							})
					else:
						return redirect('liste_produits_vendeur')

			else:
				return render(request, "Vendeur/ajouter_produit.html", {
					'categories': models.Categorie.objects.all(),
					'active': "ajouter_produit_vendeur"})

		else:
			return redirect('authentification_vendeur')

	def supprimer_produit(request, id_produit):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				try:
					produit_a_supprimer = models.Produit.objects.get(pk = id_produit, vendeur = vendeur)
				except Exception as e:
					return HttpResponse("Erreur produit introuvable, Si le problème persiste, veuillez contacter le service client au 0556748529")
				else:
					produit_a_supprimer.status = 0
					produit_a_supprimer.delete()
					return redirect('liste_produits_vendeur')

		else:
			return redirect('authentification_vendeur')

	def modifier_produit(request, id_produit):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				try:
					produit_a_modifier = models.Produit.objects.get(pk=id_produit, vendeur=vendeur)
				except Exception as e:
					return HttpResponse("Erreur produit introuvable, Si le problème persiste, veuillez contacter le service client au 0556748529")
				else:
					
					if request.method == 'POST':
						try:
							form = request.POST
							form_image = request.FILES

							categorie = models.Categorie.objects.get(cle=form.get('categorie'))
							prix = float(form.get('prix_vendeur'))*(1+ categorie.commission/100.0)

							produit_a_modifier.libelle = form.get('libelle')
							produit_a_modifier.categorie = categorie
							produit_a_modifier.prix_vendeur = form.get('prix_vendeur')
							produit_a_modifier.prix = prix
							produit_a_modifier.description = form.get('description')
							produit_a_modifier.quantite = form.get('quantite')

							# On modifie la visibilite du produit par les clients
							if form.get('status') == 'on' or form.get('status') == True:
								produit_a_modifier.status = 1
							else:
								produit_a_modifier.status = 0

							if form_image.get('image'):
								produit_a_modifier.image = form_image.get('image')

						except Exception as e:
							return HttpResponse("Erreur, Si le problème persiste, veuillez contacter le service client au 0556748529")
						else:
							produit_a_modifier.save()
							return redirect("liste_produits_vendeur")
					else:
						# On aura besoin des categories dans le template pour le choix de la categorie
						categories = models.Categorie.objects.all()
						produit = models.Produit.objects.get(pk = id_produit, vendeur=vendeur)
						return render(request, "Vendeur/modifier_produit.html", {'produit': produit, 'categories':categories})
		else:
			return redirect('authentification_vendeur')

	# Definir si le produit peut etre vue ou non par l'utilisateur
	def changer_status_produit(request, id_produit):


		if request.user.is_authenticated:

			if request.method == 'POST':

				try:
					vendeur = models.Vendeur.objects.get(user=request.user)

				except Exception as e:
					return redirect('authentification_vendeur')
				else:
					try:
						produit_a_modifier = models.Produit.objects.get(pk= id_produit, vendeur=vendeur)
					except Exception as e:
						return HttpResponse("Erreur produit introuvable, Si le problème persiste, veuillez contacter le service client au 0556748529")
					else:
						if  request.POST.get('status') is not None:
							produit_a_modifier.status = True
						else:
							produit_a_modifier.status = False
						produit_a_modifier.save()

						return redirect('dashboard_vendeur')

			else:
				return redirect('dashboard_vendeur')
		else:
			return redirect('authentification_vendeur')

	def detail_produit(request, id_produit):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				try:
					produit = models.Produit.objects.get(pk=id_produit, vendeur=vendeur)
					image_produit = models.ImageProduit.objects.filter(produit=produit)
				except Exception as e:
					return HttpResponse("Erreur produit introuvable, Si le problème persiste, veuillez contacter le service client au 0556748529")
				else:
					return render(request, "Vendeur/detail_produit.html", {'produit': produit, 'image_produit':image_produit})

		else:
			return redirect('authentification_vendeur')

	# Ajouter une image supplementaire a un produit
	def ajouter_image_produit(request, id_produit):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:

				try:
					produit = models.Produit.objects.get(pk=id_produit, vendeur=vendeur)
					models.ImageProduit.objects.create(produit=produit, image=request.FILES.get('image'))
				except Exception as e:
					return redirect('detail_produit_vendeur', id_produit)
				else:
					return redirect('detail_produit_vendeur', id_produit)

		else:
			return redirect('authentification_vendeur')

	def supprimer_image_produit(request, id_image):

		if request.user.is_authenticated:

			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				try:
					image_produit_a_supprimer = models.ImageProduit.objects.get(pk=id_image)
					produit = models.Produit.objects.get(vendeur=vendeur, imageproduit=image_produit_a_supprimer)
				except Exception as e:
					return redirect('dashboard_vendeur')
				else:
					image_produit_a_supprimer.delete()
					return redirect('detail_produit_vendeur', produit.pk)

		else:
			return redirect('authentification_vendeur')

	def modifier_infos_vendeur(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				if request.method == 'POST':

					form = request.POST
					if form.get('mdp') == form.get('c_mdp'):
						if len(form.get('mdp')) >= 6:
							try:
								vendeur.user.set_password(form.get('mdp'))
								vendeur.user.email = form.get('email')
								vendeur.contact1 = form.get('contact1')
								vendeur.contact2 = form.get('contact2')
								vendeur.ville = form.get('ville')
								vendeur.commune = form.get('commune')
								vendeur.quartier = form.get('quartier')
							except Exception as e:
								return HttpResponse("Erreur lors de la modification, Si le problème persiste, veuillez contacter le service client au 0556748529")
							else:
								vendeur.user.save()
								vendeur.save()

								return redirect('deconnexion_vendeur')
						else:
							return render(request,  "Vendeur/modifier_infos_vendeur.html", {'vendeur': vendeur, 
								'message': "Le mot de passe doit etre superieur a 6 caracteres", 'active':"parametres"})
					else:
							return render(request,  "Vendeur/modifier_infos_vendeur.html", {'vendeur': vendeur, 
								'message': "Les mots de passes ne correspondent pas", 'active':"parametres"})
				else:
					return render(request, "Vendeur/modifier_infos_vendeur.html", {'vendeur': vendeur, 'active':"parametres"})
		else:
			return redirect('authentification_vendeur')


	def changer_profil_vendeur_s3(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification')
			else:
				print("Ici aussi")
				try:
					S3_BUCKET = os.environ.get('S3_BUCKET')
					print(f"s3 bucket : {S3_BUCKET}")
					file_name = request.POST.get('file_name')
					file_type = request.POST.get('file_type')

					s3 = boto3.client('s3')

					# s3 = boto3.client('s3', config = Config(signature_version = 's3v4'))
					print("Ici")
					presigned_post = s3.generate_presigned_post(
						Bucket = S3_BUCKET,
						Key = file_name,
						Fields = {"acl": "public-read", "Content-Type": file_type},
					    Conditions = [
					      {"acl": "public-read"},
					      {"Content-Type": file_type}
					    ],
					    ExpiresIn = 3600
					)
				except Exception as e:
					raise e
				else:
					return JsonResponse({
								'data': presigned_post,
								'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
							})


	def changer_profil_vendeur(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				if request.method == 'POST':

					form_profil = request.FILES
					
					try:
						print(form_profil.get('avatar-url'))
						vendeur.profil = form_profil.get('avatar-url')
						vendeur.save()
					except Exception as e:
						return HttpResponse(
							"Erreur lors de la mise à jour du profil, Si le problème persiste, veuillez contacter le service client au 0556748529")
					else:
						return render(request, "Vendeur/modifier_infos_vendeur.html", {
							'vendeur': vendeur, 'message': "Votre profil a ete mis a jour",
							'active':"parametres"})
				else:
					return render(request, "Vendeur/modifier_infos_vendeur.html", {
						'vendeur': vendeur,
						'active': "parametres"})
		else:
			return redirect('authentification_vendeur')

	# Chaque vendeur a dans son dashboard, l'historique de ses ventes
	def historique_paiement(request):

		if request.user.is_authenticated:
			try:
				vendeur = models.Vendeur.objects.get(user=request.user)
			except Exception as e:
				return redirect('authentification_vendeur')
			else:
				historiques = models.Historique.objects.filter(vendeur = request.user)
				return render(request, "Vendeur/historique_paiement.html", {
					'historiques': historiques,
					'active': "historique_paiement_vendeur"})
		else:
			return redirect('authentification_vendeur')

def mot_de_passe_oublie(request):

	if request.method == 'POST':
		form = request.POST
		try:
			user = User.objects.get(username=form.get('username'), email=form.get('email'))
		except Exception as e:
			return render(request, "mot_de_passe_oublie.html", {'message': "Cet utilisateur n'existe pas."})
		else:
			if form.get('mdp') == form.get('c_mdp'):

				if len(form.get('mdp')) >= 6:
					user.set_password(form.get('mdp'))
					user.save()
					try:
						vendeur = models.Vendeur.objects.get(user=user)
					except Exception as e:
						return render(request, "Client/authentification.html", {'message': "Votre mot de passe à été mis à jour."})
					else:
						return render(request, "Vendeur/authentification.html", {'message': "Votre mot de passe à été mis à jour."})
				else:
					return render(request, "mot_de_passe_oublie.html", {'message': "Le mot de passe doit contenir au moins 6 caracteres.", 'form': form})
			else:
				return render(request, "mot_de_passe_oublie.html", {'message': "Les mots de passe saisient ne correspondent pas", 'form': form})

	else:
		return render(request, "mot_de_passe_oublie.html")