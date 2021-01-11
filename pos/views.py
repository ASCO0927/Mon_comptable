from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
import json
from .models import HistoriqueTransactionsClient, Client, Depot, Article, Vente, Sortie, Avarie, Entree, Controle, Categorie, Coupures, OperationsCaisse, Caisse
from django.utils import timezone
from django.contrib.auth.models import Permission, User
from django.core import serializers
from datetime import datetime



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
            if request.is_ajax():
                controles = []
                for item in liste_controle:
                    controles.append({'date_debut': item.date_debut, 'date_fin': item.date_fin})
                return JsonResponse({"liste_controle": controles},status=200)
            else:
                context = {'liste_controle': Controle.objects.all()}
                return render(request, 'pos/le_point.html', context)
        elif request.is_ajax() and request.method == 'POST':
            art_vendus = []
            controle = Controle(controleur=User.objects.get(id=user_id), date_debut=request.POST['debut'], date_fin=request.POST['fin'])
            controle.save()

            sorties = Sortie.objects.filter(numero_vente__date_vente__range=[controle.date_debut, controle.date_fin])
            for i, sortie in enumerate(sorties):
                unique = True
                for j, a in enumerate(art_vendus):
                    if(a['nom_article'] == sortie.article.nom_article):
                        art_vendus[j]['quantite'] = art_vendus[j]['quantite'] + sortie.quantite
                        unique = False
                if unique:
                    art_vendus.append({'categorie': sortie.article.categorie.nom_categorie, 'nom_article': sortie.article.nom_article, 'prix': sortie.article.PVU, 'quantite': sortie.quantite, 'benefice': sortie.quantite * (int(sortie.article.PVU) - int(sortie.article.PAU)) })
            
            benefice_periode = 0
            for vente in art_vendus:
                benefice_periode += vente['benefice']

            return JsonResponse({'date_debut': controle.date_debut, 'date_fin': controle.date_fin, 'art_vendus': art_vendus, 'benefice_periode': benefice_periode}, status=200)


################CLIENT#########################

def list_clients(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_clients = Client.objects.all()
            return render(request, 'pos/client/liste_clients.html', {'liste_clients': liste_clients})


def nouveau_client(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/client/nouveau_client.html')
        else:
            if request.is_ajax():
                client = Client(nom=request.POST['nom_client'], prenoms=request.POST['prenoms_client'], numero_cnib=request.POST['numero_cnib_client'])
                client.save()
                
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def lst_transactions_client(request, client_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            liste_depots_client = Depot.objects.filter(client = client)
            liste_transactions_client = HistoriqueTransactionsClient.objects.filter(client = client)

            liste_ventes_au_client = Vente.objects.filter(client = client)

            liste_details_vente = []

            for vente in liste_ventes_au_client:
                liste_articles_vente = []
                montant_vente = 0
                sorties = Sortie.objects.filter(numero_vente=vente.id)
                for sortie in sorties:
                    liste_articles_vente.append({'nom_article': sortie.article.nom_article, 'prix': sortie.article.PVU, 'quantite': sortie.quantite})
                    montant_vente = montant_vente + sortie.article.PVU * sortie.quantite
                hist_trans = HistoriqueTransactionsClient.objects.get(vente = vente)
                solde_avant = hist_trans.solde_avant
                solde_apres = hist_trans.solde_apres
                liste_details_vente.append(
                    {
                        'id': vente.id, 
                        'vendeur': vente.vendeur.username, 
                        'jour': vente.date_vente.strftime("%d/%m/%Y"), 
                        'heure': vente.date_vente.strftime("%H:%M"), 
                        'solde_avant': solde_avant , 
                        'solde_apres': solde_apres, 
                        'articles':liste_articles_vente, 
                        'montant_vente': montant_vente
                    }
                )

            liste_details_depot = []
            for depot in liste_depots_client:
                hist_trans = HistoriqueTransactionsClient.objects.get(depot = depot)
                solde_avant = hist_trans.solde_avant
                solde_apres = hist_trans.solde_apres
                liste_details_depot.append(
                    {
                        'id': depot.id,  
                        'jour': depot.date_depot.strftime("%d/%m/%Y"), 
                        'heure': depot.date_depot.strftime("%H:%M"), 
                        'solde_avant': solde_avant , 
                        'solde_apres': solde_apres, 
                        'montant': depot.montant,
                    }
                )


            return render(request, 'pos/transactions/liste_transactions.html', {'liste_details_depot': liste_details_depot, 'liste_details_vente': liste_details_vente})

def mod_client(request, client_id, *args, **kwargs):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            return render(request, 'pos/client/modifier_client.html', {'client': client})
        else:
            if request.is_ajax():
                client=Client.objects.get(pk = client_id)
                
                client.nom = request.POST['nom_client']
                client.prenoms = request.POST['prenoms_client']
                client.numero_cnib = request.POST['numero_cnib_client']
                client.save()
                                
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def sup_client(request, client_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            client.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def depot_client(request, client_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            return render(request, 'pos/client/depot_client.html', {"client": client})
        else:
            if request.is_ajax() and request.method == 'POST':
                
                montant_depot = int(request.POST['montant'])

                depot = Depot(client=Client.objects.get(pk = request.POST['client_id']), montant=montant_depot, date_depot=timezone.now())
                depot.save()

                #maj solde
                client=Client.objects.get(pk = client_id)
                solde_avant = int(client.solde)
                solde_apres = solde_avant + montant_depot
                client.solde = solde_apres
                client.save()

                #hist transact
                hist_transac = HistoriqueTransactionsClient(client=client, montant = montant_depot, type_transaction="depot", depot=depot, solde_avant=solde_avant, solde_apres=solde_apres, date_transaction=datetime.now())
                hist_transac.save()

                caisse_list = Caisse.objects.all()
                if len(caisse_list) == 0:
                    caisse = Caisse(montant=0)
                else:
                    caisse = caisse_list[0]
                caisse.montant += montant_depot
                caisse.save()

                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)
###################FIN CLIENT####################

def collecte_caisse(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        caisse_list = Caisse.objects.all()
        if len(caisse_list) == 0:
            caisse = Caisse(montant=0)
        else:
            caisse = caisse_list[0]

        if request.method == 'POST':
            montant_decaissement = request.POST['montant_decaissement']
            now = timezone.now()
            
            caisse.montant -= int(montant_decaissement)
            caisse.save()
            
            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
        else:
            if request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
            else:
                return render(request, 'pos/collecte_caisse.html')


def depot_petite_monnaie(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        caisse_list = Caisse.objects.all()
        if len(caisse_list) == 0:
            caisse = Caisse(montant=0)
        else:
            caisse = caisse_list[0]

        if request.method == 'POST':
            montant_encaissement = request.POST['montant_encaissement']
            now = timezone.now()
            
            caisse.montant += int(montant_encaissement)
            caisse.save()

            
            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
        else:
            if request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
            else:
                return render(request, 'pos/depot_petite_monnaie.html')


def vente(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'POST':
            liste_articles_a_vendre = request.POST['liste_articles_a_vendre']
            
            if request.POST['client_id'] != '':
                client = Client.objects.get(id=request.POST['client_id'])
            
            mode_paiement = request.POST['mode_paiement']
            now = timezone.now()

            caisse_list = Caisse.objects.all()
            if len(caisse_list) == 0:
                caisse = Caisse(montant=0)
            else:
                caisse = caisse_list[0]
            
            
            for article in json.loads(liste_articles_a_vendre):
                article_a_vendre = Article.objects.get(nom_article = article)
                quantite = json.loads(liste_articles_a_vendre)[article]
                if quantite_en_stock(article_a_vendre) < quantite:
                    return HttpResponse('la vente a echouee. Stock de {} insuffisant.'.format(article))

            if request.POST['client_id'] != '':
                vente = Vente(vendeur=User.objects.get(id=user_id), date_vente=now, client=client)
            else:
                vente = Vente(vendeur=User.objects.get(id=user_id), date_vente=now)
            vente.save()

            montant_vente = 0
            for article in json.loads(liste_articles_a_vendre):
                article_a_vendre = Article.objects.get(nom_article = article)
                quantite_a_vendre = json.loads(liste_articles_a_vendre)[article]
                prix_article = article_a_vendre.PVU

                montant_vente += quantite_a_vendre * prix_article
                #caisse.montant += quantite_a_vendre * prix_article

                sortie = Sortie(article=article_a_vendre, quantite=quantite_a_vendre, numero_vente=vente)
                sortie.save()

            #maj solde
            if request.POST['client_id'] != '':
                if mode_paiement == 'compte':
                    solde_avant = int(client.solde)
                    solde_apres = solde_avant - montant_vente
                    client.solde = solde_apres
                    client.save()
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

            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
        else:
            if request.is_ajax():
                
                caisse_list = Caisse.objects.all()
                if len(caisse_list) == 0:
                    caisse = Caisse(montant=0)
                    caisse.save()
                else:
                    caisse = caisse_list[0]

                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
            else:
                liste_articles_en_catalogue = catalogue_et_stock()
                liste_clients = Client.objects.all()

                context = {'liste_articles_en_catalogue': liste_articles_en_catalogue, 'liste_clients': liste_clients}
                return render(request, 'pos/vente.html', context)


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
            return render(request, 'pos/ctrl_vente.html', {'liste_ventes': liste_ventes})
        else:
            if request.is_ajax():
                liste_articles_vente = []
                montant_vente = 0

                sorties = Sortie.objects.filter(numero_vente=request.POST['id'])
                vente = Vente.objects.get(id=request.POST['id'])

                for sortie in sorties:
                    liste_articles_vente.append({'nom_article': sortie.article.nom_article, 'prix': sortie.article.PVU, 'quantite': sortie.quantite})
                    montant_vente = montant_vente + sortie.article.PVU * sortie.quantite

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

            context = {'liste_articles_en_catalogue': liste_articles_en_catalogue, 'val_stock_achat': val_stock_achat, 'val_stock_vente': val_stock_vente}
            return render(request, 'pos/ctrl_stock.html', context)


def ctrl_entree(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_entrees = []
            for entree in Entree.objects.all():
                jour = entree.date_entree.strftime("%d/%m/%Y")
                heure = entree.date_entree.strftime("%H:%M")
                liste_entrees.append({'id': entree.id, 'jour': jour, 'heure': heure, 'article': entree.article.nom_article, 'quantite': entree.quantite})
            
            liste_entrees.reverse()
            return render(request, 'pos/ctrl_entree.html', {'liste_entrees': liste_entrees})


def ctrl_article(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/ctrl_article.html', {'liste_articles': liste_articles})


def ctrl_categorie(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            return render(request, 'pos/ctrl_categorie.html', {'liste_categories': liste_categories})


def nouvelle_entree(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/nouvelle_entree.html', {'liste_articles': liste_articles})
        else:
            if request.is_ajax():
                entree = Entree(article=Article.objects.get(pk = request.POST['article_id']), quantite=request.POST['quantite'], date_entree=timezone.now())
                entree.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def nouvelle_avarie(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/avaries/nouvelle_avarie.html', {'liste_articles': liste_articles})
        else:
            if request.is_ajax():
                
                article_avarie = Article.objects.get(pk = request.POST['article_id'])
                quantite_avariee = int(request.POST['quantite'])
                stock = quantite_en_stock(article_avarie)

                if stock < quantite_avariee:
                    return JsonResponse({"status": "error", "titre":"Echec de l'Opération!", "message": "Echec de l'opération. Stock de {} insuffisant.".format(article_avarie)}, status=200)

                avarie = Avarie(article=article_avarie, quantite=quantite_avariee, date_avarie=timezone.now())
                avarie.save()
                return JsonResponse({"status": "success", "titre":"Opération réussie!", 'message': 'operation enregistrée avec succes'}, status=200)


def liste_produits_avaries(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_produits_avaries = Avarie.objects.all()
            return render(request, 'pos/avaries/liste_produits_avaries.html', {'liste_produits_avaries': liste_produits_avaries})


def nouvelle_categorie(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/nouvelle_categorie.html')
        else:
            if request.is_ajax():
                categorie = Categorie(nom_categorie=request.POST['nom_categorie'])
                categorie.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def nouvelle_article(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            return render(request, 'pos/nouvelle_article.html', {'liste_categories': liste_categories})
        else:
            if request.is_ajax():
                
                if request.POST['date_peremption'] == '' and request.POST['code_barres'] == '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        nom_article=request.POST['nom_article'], 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU']
                    )
                elif request.POST['date_peremption'] != '' and request.POST['code_barres'] == '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        #code_barres=request.POST['code_barres'], 
                        date_peremption=request.POST['date_peremption'], 
                        nom_article=request.POST['nom_article'], 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU'],
                    )
                elif request.POST['date_peremption'] == '' and request.POST['code_barres'] != '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        code_barres=request.POST['code_barres'], 
                        #date_peremption=request.POST['date_peremption'], 
                        nom_article=request.POST['nom_article'], 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU'],
                    )
                elif request.POST['date_peremption'] != '' and request.POST['code_barres'] != '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        code_barres=request.POST['code_barres'], 
                        date_peremption=request.POST['date_peremption'], 
                        nom_article=request.POST['nom_article'], 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU'],
                    )
                article.save()

                qte=int(request.POST['qte'])
                if not qte:
                    qte = 0
                    
                entree = Entree(article=article, quantite=qte, date_entree=timezone.now())
                entree.save()
                
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_article(request, user_id, article_id, *args, **kwargs):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            article=Article.objects.get(pk = article_id)
            return render(request, 'pos/mod_article.html', {'liste_categories': liste_categories, 'article': article})
        else:
            if request.is_ajax():
                article=Article.objects.get(pk = article_id)
                
                article.categorie = Categorie.objects.get(pk=request.POST['categorie_id'])
                article.nom_article = request.POST['nom_article']
                article.PAU = request.POST['PAU']
                article.PVU = request.POST['PVU']
                
                if request.POST['date_peremption'] != '':
                    article.date_peremption = request.POST['date_peremption']
                if request.POST['code_barres'] != '' and request.POST['code_barres'] != 'None':
                    article.code_barres = request.POST['code_barres']

                article.save()
                                
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def sup_article(request, user_id, article_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            article=Article.objects.get(pk = article_id)
            article.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_entree(request, user_id, entree_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            entree=Entree.objects.get(pk = entree_id)
            return render(request, 'pos/mod_entree.html', {'liste_articles': liste_articles, 'entree': entree})
        else:
            if request.is_ajax():
                entree=Entree.objects.get(pk = entree_id)
                
                entree.article = Article.objects.get(pk = request.POST['article_id'])
                entree.quantite = request.POST['quantite']
                entree.date_entree = timezone.now()
                
                entree.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def sup_entree(request, user_id, entree_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            entree=Entree.objects.get(pk = entree_id)
            entree.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_categorie(request, user_id, categorie_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            categorie=Categorie.objects.get(pk = categorie_id)
            return render(request, 'pos/mod_categorie.html', {'categorie': categorie})
        else:
            if request.is_ajax():
                categorie=Categorie.objects.get(pk = categorie_id)
                
                categorie.nom_categorie = request.POST['nom_categorie']
                
                categorie.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def sup_categorie(request, user_id, categorie_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            categorie=Categorie.objects.get(pk = categorie_id)
            categorie.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def ctrl_caisse(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/ctrl_caisse.html')


def catalogue_et_stock():
    articles_en_catalogue = Article.objects.all()
    liste_articles_en_catalogue = []

    for article in articles_en_catalogue:
        entree=Entree.objects.filter(article = article.id)

        if len(entree):
            id_derniere_entree = entree[len(entree)-1].pk
        else:
            entree = Entree(article=article, quantite=0, date_entree=timezone.now())
            entree.save()
            id_derniere_entree = entree.id


        liste_articles_en_catalogue.append({"id": article.id, "code_barres": article.code_barres, "date_peremption": article.date_peremption,  "categorie": article.categorie, "nom_article": article.nom_article, "PAU": article.PAU, "PVU": article.PVU, "en_stock": quantite_en_stock(article), "id_derniere_entree": id_derniere_entree})

    return liste_articles_en_catalogue
        

def quantite_en_stock(article_recherche):
    liste_sorties = Sortie.objects.filter(article=article_recherche)
    liste_avaries = Avarie.objects.filter(article=article_recherche)
    liste_entrees = Entree.objects.filter(article=article_recherche)
    total_sortie = 0
    total_avarie = 0
    total_entree = 0

    for sortie in liste_sorties:
        total_sortie = total_sortie + sortie.quantite
    
    for avarie in liste_avaries:
        total_avarie = total_avarie + avarie.quantite

    for entree in liste_entrees:
        total_entree = total_entree + entree.quantite
    
    return total_entree - total_sortie - total_avarie

