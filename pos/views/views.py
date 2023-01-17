import json
import logging
from datetime import datetime
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from ..models import (Article, Avarie, Caisse, Categorie, Client,
                     CompteOrangeMoney, Controle, Depot, Entree,
                     HistoriqueDepotRamassageCaisse,
                     HistoriqueDepotRamassageCompteOrangeMoney,
                     HistoriqueTransactionsClient, Sortie, Vente)

from .client import *
from .vente import *
from .entree import *
from .caisse import *
from .OM import *
from .article import *
from .avarie import *
from .categorie import *

from ..recus import enregistrer_recu_type1, enregistrer_recu_type2, enregistrer_proforma
#from getmac import get_mac_address as gma

#logging.basicConfig(filename="log.txt", encoding="utf-8", level=logging.DEBUG)

def arrondir_montants(nombre):
    return nombre
    '''
    mod = nombre%25
    if mod != 0:
        return nombre - mod
    else:
        return nombre
    '''
def generer_proforma(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'POST':
            liste_articles_a_vendre = request.POST['liste_articles_a_vendre']
            objet_facture = request.POST['objet_facture']

            if request.POST['client_id'] != '':
                client = Client.objects.get(id=request.POST['client_id'])

            mode_paiement = request.POST['mode_paiement']
            now = timezone.now()
            
            enregistrer_proforma(liste_articles_a_vendre, client, objet_facture)


            return JsonResponse({'message': 'operation effectuee avec succes'}, status=200)
        

def login_view(request):
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('pos:vente', args=(user.id,)))
        else:
            return HttpResponse('Erreur de connection')
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('pos:vente', args=(request.user.id,)))
        return render(request, 'pos/login.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('pos:login'))


def le_point(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_controle = Controle.objects.all()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                controles = []
                for item in liste_controle:
                    controles.append({'date_debut': item.date_debut, 'date_fin': item.date_fin})
                return JsonResponse({"liste_controle": controles},status=200)
            else:
                context = {'liste_controle': Controle.objects.all()}
                return render(request, 'pos/le_point.html', context)
        elif request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            print('requete lancee')
            art_vendus = []
            controle = Controle(controleur=User.objects.get(id=user_id), date_debut=request.POST['debut'], date_fin=request.POST['fin'])
            controle.save()

            sorties = Sortie.objects.filter(numero_vente__date_vente__range=[controle.date_debut, controle.date_fin])
            for i, sortie in enumerate(sorties):

                unique = True
                for j, a in enumerate(art_vendus):
                    if(a['nom_article'] == sortie.article.nom_article):
                        art_vendus[j]['quantite'] = art_vendus[j]['quantite'] + sortie.quantite
                        art_vendus[j]['montant_vente'] = art_vendus[j]['montant_vente'] + arrondir_montants(sortie.quantite * sortie.prix_vente_article)
                        art_vendus[j]['benefice'] = art_vendus[j]['benefice'] + arrondir_montants(sortie.quantite * sortie.prix_vente_article) - (sortie.quantite * sortie.article.PAU)
                        unique = False
                if unique:
                    art_vendus.append({
                        'categorie': sortie.article.categorie.nom_categorie, 
                        'nom_article': sortie.article.nom_article, 
                        'PAU': sortie.article.PAU, 
                        'PVU': sortie.article.PVU, 
                        'quantite': sortie.quantite,
                        'montant_vente': arrondir_montants(sortie.quantite * sortie.prix_vente_article),
                        'benefice': arrondir_montants(sortie.quantite * sortie.prix_vente_article) - (sortie.quantite * sortie.article.PAU)
                        })

            

            benefice_periode = 0
            for vente in art_vendus:
                benefice_periode += vente['benefice']
            

            return JsonResponse({'date_debut': controle.date_debut, 'date_fin': controle.date_fin, 'art_vendus': art_vendus, 'benefice_periode': benefice_periode}, status=200)


def ctrl_stock(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles_en_catalogue = catalogue_et_stock()
            val_stock_achat = 0
            val_stock_vente = 0

            for article in liste_articles_en_catalogue:
                val_stock_achat += (article['PAU'] * article['en_stock'])
                val_stock_vente += (article['PVU'] * article['en_stock'])

            context = {'liste_articles_en_catalogue': liste_articles_en_catalogue, 'val_stock_achat': arrondir_montants(val_stock_achat), 'val_stock_vente': arrondir_montants(val_stock_vente)}
            return render(request, 'pos/ctrl_stock.html', context)
