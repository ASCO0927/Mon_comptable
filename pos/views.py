from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
import json
from .models import Article, Vente, Sortie, Avarie, Entree, Controle, Categorie, Coupures, OperationsCaisse
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
                    art_vendus.append({'categorie': sortie.article.categorie.nom_categorie, 'nom_article': sortie.article.nom_article, 'prix': sortie.article.PVU, 'quantite': sortie.quantite})
                        

            return JsonResponse({'date_debut': controle.date_debut, 'date_fin': controle.date_fin, 'art_vendus': art_vendus}, status=200)


def collecte_caisse(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'POST':
            detail_encaissement = request.POST['detail_encaissement']
            now = timezone.now()
            
            operation_caisse = OperationsCaisse(type_operation='decaissement', motif='ramassage', date_operation=now)
            operation_caisse.save()
            for det_enc in json.loads(detail_encaissement):
                if(det_enc['qte']):
                    ncoupure = Coupures(operation_caisse=operation_caisse, coupure=det_enc['coupure'], qte=det_enc['qte'])
                    ncoupure.save()
            
            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': Caisse()}, status=200)
        else:
            if request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': Caisse()}, status=200)
            else:
                return render(request, 'pos/collecte_caisse.html')




def depot_petite_monnaie(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'POST':
            detail_encaissement = request.POST['detail_encaissement']
            now = timezone.now()
            
            operation_caisse = OperationsCaisse(type_operation='encaissement', motif='depot_petite_monnaie', date_operation=now)
            operation_caisse.save()
            for det_enc in json.loads(detail_encaissement):
                if(det_enc['qte']):
                    ncoupure = Coupures(operation_caisse=operation_caisse, coupure=det_enc['coupure'], qte=det_enc['qte'])
                    ncoupure.save()
            
            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': Caisse()}, status=200)
        else:
            if request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': Caisse()}, status=200)
            else:
                return render(request, 'pos/depot_petite_monnaie.html')



def vente(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'POST':
            liste_articles_a_vendre = request.POST['liste_articles_a_vendre']
            montant_encaisse = request.POST['montant_encaisse']
            monnaie_rendue = request.POST['monnaie_rendue']
            detail_encaissement = request.POST['detail_encaissement']
            detail_monnaie_a_rendre = request.POST['detail_monnaie_a_rendre']
            now = timezone.now()
            
            for article in json.loads(liste_articles_a_vendre):
                article_a_vendre = Article.objects.get(nom_article = article)
                quantite = json.loads(liste_articles_a_vendre)[article]
                if quantite_en_stock(article_a_vendre) < quantite:
                    return HttpResponse('la vente a echouee. Stock de {} insuffisant.'.format(article))

            vente = Vente(vendeur=User.objects.get(id=user_id), date_vente=now, montant_encaisse=montant_encaisse, monnaie_rendue=monnaie_rendue)
            vente.save()

            for article in json.loads(liste_articles_a_vendre):
                sortie = Sortie(article=Article.objects.get(nom_article = article), quantite=json.loads(liste_articles_a_vendre)[article], numero_vente=vente)
                sortie.save()
            
            operation_caisse = OperationsCaisse(type_operation='encaissement', motif='vente', numero_vente=vente, date_operation=now)
            operation_caisse.save()
            for det_enc in json.loads(detail_encaissement):
                if(det_enc['qte']):
                    ncoupure = Coupures(operation_caisse=operation_caisse, coupure=det_enc['coupure'], qte=det_enc['qte'])
                    ncoupure.save()
            
            operation_caisse_d = OperationsCaisse(type_operation='decaissement', motif='vente', numero_vente=vente, date_operation=now)
            operation_caisse_d.save()
            for det_monnaie in json.loads(detail_monnaie_a_rendre):
                if(det_monnaie['qte']):
                    ncoupure = Coupures(operation_caisse=operation_caisse_d, coupure=det_monnaie['coupure'], qte=det_monnaie['qte'])
                    ncoupure.save()
            
            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': Caisse()}, status=200)
        else:
            if request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': Caisse()}, status=200)
            else:
                liste_articles_en_catalogue = catalogue_et_stock()

                context = {'liste_articles_en_catalogue': liste_articles_en_catalogue}
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

                return JsonResponse({'id': request.POST['id'], 'vendeur': vente.vendeur.username, 'jour': vente.date_vente.strftime("%d/%m/%Y"), 'heure': vente.date_vente.strftime("%H:%M"), 'montant_encaisse': vente.montant_encaisse , 'monnaie_rendue': vente.monnaie_rendue, 'articles':liste_articles_vente, 'montant_vente': montant_vente}, status=200)


def ctrl_stock(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles_en_catalogue = catalogue_et_stock()

            context = {'liste_articles_en_catalogue': liste_articles_en_catalogue}
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
    if not request.user.is_authenticated:
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


def avarie(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/avarie.html', {'liste_articles': liste_articles})
        else:
            if request.is_ajax():
                avarie = Avarie(article=Article.objects.get(pk = request.POST['article_id']), quantite=request.POST['quantite'], date_avarie=timezone.now())
                avarie.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def nouvelle_categorie(request, user_id):
    if not request.user.is_authenticated:
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            return render(request, 'pos/nouvelle_article.html', {'liste_categories': liste_categories})
        else:
            if request.is_ajax():
                article = Article(categorie=Categorie.objects.get(pk=request.POST['categorie_id']), nom_article=request.POST['nom_article'], PAU=request.POST['PAU'], PVU=request.POST['PVU'])
                article.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_article(request, user_id, article_id):
    if not request.user.is_authenticated:
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
                
                article.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def sup_article(request, user_id, article_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            article=Article.objects.get(pk = article_id)
            article.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def mod_entree(request, user_id, entree_id):
    if not request.user.is_authenticated:
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            entree=Entree.objects.get(pk = entree_id)
            entree.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_categorie(request, user_id, categorie_id):
    if not request.user.is_authenticated:
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            categorie=Categorie.objects.get(pk = categorie_id)
            categorie.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def ctrl_caisse(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/ctrl_caisse.html')


def catalogue_et_stock():
    articles_en_catalogue = Article.objects.all()
    liste_articles_en_catalogue = []

    for article in articles_en_catalogue:
        liste_articles_en_catalogue.append({"categorie": article.categorie, "nom_article": article.nom_article, "PAU": article.PAU, "PVU": article.PVU, "en_stock": quantite_en_stock(article)})

    return liste_articles_en_catalogue;
        

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


def Caisse():
    caisse = [
        {
            'coupure': 5,
            'qte': 0
        },
        {
            'coupure': 10,
            'qte': 0,
        },
        {
            'coupure': 25,
            'qte': 0,
        },
        {
            'coupure': 50,
            'qte': 0,
        },
        {
            'coupure': 100,
            'qte': 0,
        },
        {
            'coupure': 200,
            'qte': 0,
        },
        {
            'coupure': 250,
            'qte': 0,
        },
        {
            'coupure': 500,
            'qte': 0,
        },
        {
            'coupure': 1000,
            'qte': 0,
        },
        {
            'coupure': 2000,
            'qte': 0,
        },
        {
            'coupure': 5000,
            'qte': 0,
        },
        {
            'coupure': 10000,
            'qte': 0,
        },
    ]

    coupures = Coupures.objects.all()

    for coupure in coupures:
        if coupure.operation_caisse.type_operation == 'encaissement':
            for i, elt in enumerate(caisse):
                if elt['coupure'] == coupure.coupure:
                    caisse[i]['qte'] += coupure.qte
        else:
            for i, elt in enumerate(caisse):
                if elt['coupure'] == coupure.coupure:
                    caisse[i]['qte'] -= coupure.qte
    caisse.reverse()
    return caisse