from ast import Try
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

from ..models import (Article, Caisse, Client,
                     CompteOrangeMoney,
                     HistoriqueTransactionsClient, Sortie, Vente)

from ..recus import enregistrer_recu_type1, enregistrer_recu_type2
from .utils import *

def _procedure_annulation_vente(id_vente):
    montant_vente = 0

    # sorties = Sortie.objects.filter(numero_vente=int(request.POST['id']))
    # vente = Vente.objects.get(id=int(request.POST['id']))
    sorties = Sortie.objects.filter(numero_vente=int(id_vente))
    vente = Vente.objects.get(id=int(id_vente))


    for sortie in sorties:
        montant_vente = montant_vente + sortie.prix_vente_article * sortie.quantite

    #caisse
    caisse_list = Caisse.objects.all()
    if len(caisse_list) == 0:
        caisse = Caisse(montant=0)
    else:
        caisse = caisse_list[0]
    #orange money
    compte_orange_money_list = CompteOrangeMoney.objects.all()
    if len(compte_orange_money_list) == 0:
        compte_orange_money = CompteOrangeMoney(montant=0)
    else:
        compte_orange_money = compte_orange_money_list[0]
                
    try:
        hist_trans = HistoriqueTransactionsClient.objects.get(vente = vente)
    except HistoriqueTransactionsClient.DoesNotExist:
        hist_trans = None
    
    if hist_trans is None:
        raise Exception("HistoriqueTransactionsClient.DoesNotExist")

    if hist_trans.type_transaction == "compte":
        client = Client.objects.get(id=hist_trans.client.id)
        solde_avant = int(client.solde)
        solde_apres = solde_avant + montant_vente
        client.solde = solde_apres
        client.save()
    elif hist_trans.type_transaction == "liquide":
        #maj caisse
        caisse.montant -= montant_vente
        caisse.save()
    elif hist_trans.type_transaction == "orange_money":
        #maj compte_orange_money
        compte_orange_money.montant -= montant_vente
        compte_orange_money.save()
            
    hist_trans.delete()

    vente.delete()

    return caisse, compte_orange_money


def _procedure_de_vente():
    pass


def modifier_vente(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    if request.method == 'GET':
        
        try:
            id_vente = int(request.GET.get('id_vente',''))
        except:
            return render(request, 'pos/page_not_found.html')
        
        
        sorties = Sortie.objects.filter(numero_vente=id_vente)
        if len(sorties) == 0:
            return render(request, 'pos/page_not_found.html')
        
        liste_articles_en_catalogue = catalogue_et_stock()
        liste_clients = Client.objects.all()
        context = {'liste_articles_en_catalogue': liste_articles_en_catalogue, 'liste_clients': liste_clients, 'liste_sorties': sorties, 'id_vente': id_vente}
        
        return render(request, 'pos/vente/mod_vente.html', context)
    else:
        id_vente = request.POST.get('id_vente','')
        _procedure_annulation_vente(id_vente)
        vente(request, user_id)


def annuler_vente(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            caisse, compte_orange_money = _procedure_annulation_vente(request.POST['id'])
            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant, 'orange_money': compte_orange_money.montant}, status=200)


def vente(request, user_id):
    #print(gma.upper()) gma().upper() != 'D0:67:E5:1A:A7:B0' or 
    if date.today() > date(2023, 8, 15):
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'POST':
            liste_articles_a_vendre = request.POST.get('liste_articles_a_vendre', [])

            if request.POST['monnaie_rendue'].isnumeric():
                monnaie_rendue = request.POST['monnaie_rendue']
            else:
                monnaie_rendue = 0
            if request.POST['montant_encaisse'].isnumeric():
                montant_encaisse = request.POST['montant_encaisse']
            else:
                montant_encaisse = 0

            if request.POST['client_id'] != '':
                client = Client.objects.get(id=request.POST['client_id'])

            mode_paiement = request.POST['mode_paiement']
            now = timezone.now()

            #caisse
            caisse_list = Caisse.objects.all()
            if len(caisse_list) == 0:
                caisse = Caisse(montant=0)
            else:
                caisse = caisse_list[0]

            #orange money
            compte_orange_money_list = CompteOrangeMoney.objects.all()
            if len(compte_orange_money_list) == 0:
                compte_orange_money = CompteOrangeMoney(montant=0)
            else:
                compte_orange_money = compte_orange_money_list[0]


            for article in json.loads(liste_articles_a_vendre):
                article_a_vendre = Article.objects.get(nom_article = article["article"])
                quantite = article["quantite"]
                if quantite_en_stock(article_a_vendre) < int(quantite):
                    return HttpResponse('la vente a echouee. Stock de {} insuffisant.'.format(article))

            if request.POST['client_id'] != '':
                vente = Vente(vendeur=User.objects.get(id=user_id), montant_encaisse=montant_encaisse, monnaie_rendue=monnaie_rendue, date_vente=now, client=client)
            else:
                vente = Vente(vendeur=User.objects.get(id=user_id), montant_encaisse=montant_encaisse, monnaie_rendue=monnaie_rendue, date_vente=now)
            vente.save()

            montant_vente = 0
            for article in json.loads(liste_articles_a_vendre):
                article_a_vendre = Article.objects.get(nom_article = article["article"])
                quantite_a_vendre = article["quantite"]
                prix_article = float(article["prix"])

                montant_vente += int(quantite_a_vendre) * prix_article

                sortie = Sortie(article=article_a_vendre, quantite=quantite_a_vendre, prix_vente_article=float(prix_article), numero_vente=vente)
                sortie.save()

            #maj solde
            if request.POST['client_id'] != '':
                if mode_paiement == 'compte':
                    solde_avant = int(client.solde)
                    solde_apres = solde_avant - montant_vente
                    client.solde = solde_apres
                    client.save()
                elif mode_paiement == 'orange_money':
                    solde_avant = int(client.solde)
                    solde_apres = int(client.solde)

                    #maj compte orange money
                    compte_orange_money.montant += montant_vente
                    compte_orange_money.save()
                elif mode_paiement == 'liquide':
                    solde_avant = int(client.solde)
                    solde_apres = int(client.solde)

                    #maj caisse
                    caisse.montant += montant_vente
                    caisse.save()
                else:
                    return HttpResponse('Echec de la transaction! le mode de paiment {} n est pas connu du systeme'.format(mode_paiement))
            else:
                #maj caisse
                caisse.montant += montant_vente
                caisse.save()

            #hist transact
            if request.POST['client_id'] != '':
                hist_transac = HistoriqueTransactionsClient(client=client, montant = montant_vente, type_transaction=mode_paiement, vente=vente, solde_avant=solde_avant, solde_apres=solde_apres, date_transaction=datetime.now())
                hist_transac.save()

            #generation de la facture
            type_recu = 1
            if type_recu == 1:
                enregistrer_recu_type1(liste_articles_a_vendre, client)
            else:
                if int(montant_encaisse) == 0:
                    enregistrer_recu_type2(liste_articles_a_vendre, montant_vente, monnaie_rendue)
                else:
                    enregistrer_recu_type2(liste_articles_a_vendre, montant_encaisse, monnaie_rendue)
            #fin facture

            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant, 'orange_money': compte_orange_money.montant}, status=200)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                
                #caisse
                caisse_list = Caisse.objects.all()
                if len(caisse_list) == 0:
                    caisse = Caisse(montant=0)
                    caisse.save()
                else:
                    caisse = caisse_list[0]
                
                #orange money
                compte_orange_money_list = CompteOrangeMoney.objects.all()
                if len(compte_orange_money_list) == 0:
                    compte_orange_money = CompteOrangeMoney(montant=0)
                else:
                    compte_orange_money = compte_orange_money_list[0]

                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant, 'orange_money': compte_orange_money.montant}, status=200)
            else:
                liste_articles_en_catalogue = catalogue_et_stock()
                liste_clients = Client.objects.all()

                context = {'liste_articles_en_catalogue': liste_articles_en_catalogue, 'liste_clients': liste_clients}
                return render(request, 'pos/vente/vente.html', context)


def ctrl_vente(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_ventes = []
            for vente in Vente.objects.all():
                jour = vente.date_vente.strftime("%d/%m/%Y")
                heure = vente.date_vente.strftime("%H:%M")
                liste_ventes.append({'id': vente.id, 'jour': jour, 'heure': heure})

            liste_ventes.reverse()
            return render(request, 'pos/vente/ctrl_vente.html', {'liste_ventes': liste_ventes})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                liste_articles_vente = []
                montant_vente = 0

                sorties = Sortie.objects.filter(numero_vente=request.POST['id'])
                vente = Vente.objects.get(id=request.POST['id'])

                for sortie in sorties:
                    liste_articles_vente.append({'nom_article': sortie.article.nom_article, 'prix': sortie.prix_vente_article, 'quantite': sortie.quantite})
                    montant_vente = montant_vente + sortie.prix_vente_article * sortie.quantite

                if vente.client:
                    return JsonResponse(
                        {
                            'id': request.POST['id'], 
                            'vendeur': vente.vendeur.username, 
                            'jour': vente.date_vente.strftime("%d/%m/%Y"), 
                            'heure': vente.date_vente.strftime("%H:%M"), 
                            'montant_encaisse': vente.montant_encaisse , 
                            'monnaie_rendue': vente.monnaie_rendue, 
                            'articles':liste_articles_vente, 
                            'montant_vente': montant_vente,
                            'client': '{} {}'.format(vente.client.nom, vente.client.prenoms),
                        }, 
                    status=200)
                else:
                    return JsonResponse(
                        {
                            'id': request.POST['id'], 
                            'vendeur': vente.vendeur.username, 
                            'jour': vente.date_vente.strftime("%d/%m/%Y"), 
                            'heure': vente.date_vente.strftime("%H:%M"), 
                            'montant_encaisse': vente.montant_encaisse , 
                            'monnaie_rendue': vente.monnaie_rendue, 
                            'articles':liste_articles_vente, 
                            'montant_vente': montant_vente,
                        }, 
                    status=200)
