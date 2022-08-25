from django.urls import path
from .views import views
from django.views.generic.base import RedirectView

'''
from django.utils import timezone
from .models import *
from datetime import datetime
import pandas as pd
from django.db import IntegrityError
import sqlite3
from django.utils.timezone import make_aware

def create_categorie():
	try:
	    categorie = Categorie(nom_categorie="default")
	    categorie.save()
	except:
	    print("Erreur de creation categorie")

def create_client():
	try:
	    client = Client(nom="default", prenoms="default", numero_cnib="default", solde=0)
	    client.save()
	except:
	    print("Erreur de creation client")

con = sqlite3.connect("to_migrate/db.sqlite3")
df_article = pd.read_sql_query("SELECT * from pos_article", con)
df_entree = pd.read_sql_query("SELECT * from pos_entree", con)
df_vente = pd.read_sql_query("SELECT * from pos_vente", con)
df_sortie = pd.read_sql_query("SELECT * from pos_sortie", con)

def articles_creation():
    for i in range(df_article.shape[0]):
        id = df_article.loc[i, 'id']
        nom_article = df_article.loc[i, 'nom_article']
        code_barres = df_article.loc[i, 'code_barres']
        PAU = df_article.loc[i, 'PAU']
        PVU = df_article.loc[i, 'PVU']
        categorie_id = df_article.loc[i, 'categorie_id']
        try:
            article = Article(id=id, categorie_id=categorie_id, nom_article=nom_article, PAU=float(PAU), PVU=float(PVU), code_barres=code_barres)
            article.save()
            print("article {} creee".format(article.nom_article))
        except Exception as e:
            print(e)

def entrees_creation():
    for i in range(df_entree.shape[0]):
        id = df_entree.loc[i, 'id']
        quantite = df_entree.loc[i, 'quantite']
        date_entree = df_entree.loc[i, 'date_entree']
        article_id = df_entree.loc[i, 'article_id']
        try:
            entree = Entree(id=id, quantite=quantite, date_entree=date_entree, article_id=article_id)
            entree.save()
            print('nouvelle entree : {}, {}'.format(article_id, entree.quantite))
        except Exception as e:
            print(e)

def vente_creation():
    for i in range(df_vente.shape[0]):
        id = df_vente.loc[i, 'id']
        montant_encaisse = df_vente.loc[i, 'montant_encaisse']
        monnaie_rendue = df_vente.loc[i, 'monnaie_rendue']
        vendeur_id = df_vente.loc[i, "vendeur_id"]
        client_id = df_vente.loc[i, "client_id"]
        date_vente = df_vente.loc[i, "date_vente"]
        try:
            vente = Vente(id=id, montant_encaisse=montant_encaisse, monnaie_rendue=monnaie_rendue, vendeur_id=vendeur_id, client_id=client_id, date_vente=date_vente)
            vente.save()
        except Exception as e:
            print(e)

def sortie_creation():
    for i in range(df_sortie.shape[0]):
        id = df_sortie.loc[i, 'id']
        quantite = df_sortie.loc[i, 'quantite']
        article_id = df_sortie.loc[i, 'article_id']
        numero_vente_id = df_sortie.loc[i, 'numero_vente_id']
        a = Article.objects.get(pk=article_id)
        prix_vente_article = float(a.PVU)
        try:
            sortie = Sortie(id=id, quantite=quantite, article=article_id, numero_vente_id=numero_vente_id, prix_vente_article=prix_vente_article)
            sortie.save()
        except Exception as e:
            print(f"{a.nom_article}: {e}")

create_categorie()
articles_creation()
entrees_creation()
vente_creation()
sortie_creation()
'''

app_name = 'pos'
urlpatterns = [
    path('', RedirectView.as_view(url='login/')),

    path('<int:user_id>/generer_proforma/', views.generer_proforma, name='generer_proforma'),
    path('<int:user_id>/modifier_vente/', views.modifier_vente, name='modifier_vente'),


    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:user_id>/vente/', views.vente, name='vente'),
    path('<int:user_id>/annuler_vente/', views.annuler_vente, name='annuler_vente'),


    path('<int:user_id>/nouvelle_avarie/', views.nouvelle_avarie, name='nouvelle_avarie'),
    path('<int:user_id>/avaries/', views.liste_produits_avaries, name='liste_produits_avaries'),

    
    path('<int:user_id>/controle/le_point/', views.le_point, name='le_point'),
    path('<int:user_id>/controle/vente/', views.ctrl_vente, name='ctrl_vente'),
    path('<int:user_id>/controle/caisse/', views.ctrl_caisse, name='ctrl_caisse'),
    path('<int:user_id>/controle/stock/', views.ctrl_stock, name='ctrl_stock'),
    path('<int:user_id>/controle/entrees/', views.ctrl_entree, name='ctrl_entree'),
    path('<int:user_id>/controle/articles/', views.ctrl_article, name='ctrl_article'),
    path('<int:user_id>/controle/categories/', views.ctrl_categorie, name='ctrl_categorie'),
    path('<int:user_id>/controle/nouvelle_entree/', views.nouvelle_entree, name='nouvelle_entree'),
    path('<int:user_id>/controle/nouvelle_article/', views.nouvelle_article, name='nouvelle_article'),
    path('<int:user_id>/controle/nouvelle_categorie/', views.nouvelle_categorie, name='nouvelle_categorie'),
    path('<int:user_id>/controle/depot_petite_monnaie/', views.depot_petite_monnaie, name='depot_petite_monnaie'),
    path('<int:user_id>/controle/collecte_caisse/', views.collecte_caisse, name='collecte_caisse'),
    
    path('<int:user_id>/mod/article/<int:article_id>', views.mod_article, name='mod_article'),
    path('<int:user_id>/sup/article/<int:article_id>', views.sup_article, name='sup_article'),
    path('<int:user_id>/mod/categorie/<int:categorie_id>', views.mod_categorie, name='mod_categorie'),
    path('<int:user_id>/sup/categorie/<int:categorie_id>', views.sup_categorie, name='sup_categorie'),
    path('<int:user_id>/mod/entree/<int:entree_id>', views.mod_entree, name='mod_entree'),
    path('<int:user_id>/sup/entree/<int:entree_id>', views.sup_entree, name='sup_entree'),

    path('lst/client/', views.list_clients, name='lst_client'),
    path('nvo/client/', views.nouveau_client, name='nouveau_client'),
    path('mod/client/<int:client_id>', views.mod_client, name='mod_client'),
    path('sup/client/<int:client_id>', views.sup_client, name='sup_client'),

    path('lst/transactions/<int:client_id>', views.lst_transactions_client, name='lst_transactions_client'),

    path('avance/<int:client_id>', views.depot_client, name='avance_client'),
    
    #DEBUT ORANGE MONEY
    path('<int:user_id>/controle/depot_caisse_orange_money/', views.depot_caisse_orange_money, name='depot_caisse_orange_money'),
    path('<int:user_id>/controle/collecte_caisse_orange_money/', views.collecte_caisse_orange_money, name='collecte_caisse_orange_money'),
    #FIN ORANGE MONEY
]
