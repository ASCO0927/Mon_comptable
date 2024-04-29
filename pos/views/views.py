from django_datatables_view.base_datatable_view import BaseDatatableView
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
from django.db.models import Subquery, OuterRef, Q, Sum
from ..models import (Article, Avarie, Caisse, Categorie, Client,
                     CompteOrangeMoney, Controle, Depot, Entree,
                     HistoriqueDepotRamassageCaisse,
                     HistoriqueDepotRamassageCompteOrangeMoney,
                     HistoriqueTransactionsClient, Sortie, Vente, Parametre, ArretCompte)

from .client import *
from .vente import *
from .entree import *
from .caisse import *
from .OM import *
from .article import *
from .avarie import *
from .categorie import *
from django.core import serializers

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
            return HttpResponseRedirect(reverse('pos:vente'))
        else:
            return HttpResponse('Erreur de connection')
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('pos:vente'))
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


class StockJson(BaseDatatableView):
    model = Article
    columns = ['categorie', 'nom_article', 'PAU', 'PVU', 'PVG', 'en_stock', 'id', 'categorie_id', 'id_derniere_entree']

    def render_column(self, row, column):
        if column == 'categorie':
            return str(row.categorie)
        elif column == 'nom_article':
            return str(row.nom_article)
        elif column == 'PAU':
            return str(row.PAU)
        elif column == 'PVU':
            return str(row.PVU)
        elif column == 'PVG':
            return str(row.PVG)
        elif column == 'en_stock':
            return quantite_en_stock(row)
        elif column == 'id':
            return str(row.id)
        elif column == 'categorie_id':
            return str(row.categorie.id)
        elif column == 'id_derniere_entree':
            return str(Entree.objects.filter(article=row).last().id if Entree.objects.filter(article=row).exists() else '')
        else:
            return super(StockJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(categorie__nom_categorie__icontains=sSearch) | 
                           Q(nom_article__icontains=sSearch) |
                           Q(PAU__icontains=sSearch) |
                           Q(PVU__icontains=sSearch) |
                           Q(PVG__icontains=sSearch))
        return qs
    
    def ordering(self, qs):
        # Retrieve the ordering from the query parameters
        order = self._querydict.get('order[0][dir]', 'asc')
        column = self._querydict.get('order[0][column]', '0')
        column_name = self.columns[int(column)]

        # Check if the ordering is on the `en_stock` column
        if column_name == 'en_stock':
            # Create a new queryset with the computed `en_stock` values
            new_qs = qs.annotate(
                computed_en_stock=Subquery(
                    Entree.objects.filter(article=OuterRef('pk')).annotate(total_entree=Sum('quantite')).values('total_entree')[:1]
                ) - Subquery(
                    Sortie.objects.filter(article=OuterRef('pk')).annotate(total_sortie=Sum('quantite')).values('total_sortie')[:1]
                ) - Subquery(
                    Avarie.objects.filter(article=OuterRef('pk')).annotate(total_avarie=Sum('quantite')).values('total_avarie')[:1]
                )
            )
            # Order the new queryset based on the computed `computed_en_stock` values
            if order == 'asc':
                return new_qs.order_by('computed_en_stock')
            else:
                return new_qs.order_by('-computed_en_stock')

        # Default ordering for other columns
        return super(StockJson, self).ordering(qs)

def ctrl_stock(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            val_stock_achat = 0
            val_stock_vente = 0
            """
            liste_articles_en_catalogue = catalogue_et_stock()

            for article in liste_articles_en_catalogue:
                val_stock_achat += (article['PAU'] * article['en_stock'])
                val_stock_vente += (article['PVU'] * article['en_stock'])
            """
            context = {
                #'liste_articles_en_catalogue': liste_articles_en_catalogue, 
                #'val_stock_achat': arrondir_montants(val_stock_achat), 
                #'val_stock_vente': arrondir_montants(val_stock_vente)
                }
            return render(request, 'pos/ctrl_stock.html', context)


def get_stock_value(request):
    val_stock_achat = 0
    val_stock_vente = 0
    
    liste_articles_en_catalogue = catalogue_et_stock()

    for article in liste_articles_en_catalogue:
        val_stock_achat += (article['PAU'] * article['en_stock'])
        val_stock_vente += (article['PVU'] * article['en_stock'])

    data = {
        'stock_achat_value': val_stock_achat,
        'stock_vente_detail_value': val_stock_vente,
    }

    return JsonResponse(data)


