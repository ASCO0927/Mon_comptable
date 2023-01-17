import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from ..models import (Article, Categorie, Entree)

def nouvelle_article(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            return render(request, 'pos/nouvelle_article.html', {'liste_categories': liste_categories})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                nom_article=request.POST['nom_article'].strip()

                if 'PAU' in request.POST.keys() and request.POST['PAU']:
                    try:
                        PAU=float(request.POST['PAU'])
                    except Exception as e:
                        logging.exception("Le prix d'achat unitaire doit etre un nombre")
                        return JsonResponse({'message': "Le prix d'achat unitaire doit etre un nombre"}, status=510)
                else:
                    logging.exception("Le champ PAU est obligatoire")
                    print(request.POST['PAU'])
                    return JsonResponse({'message': "Le champ PAU est obligatoire"}, status=510)
                
                if 'PVU' in request.POST.keys() and  request.POST['PVU']:
                    try:
                        PVU=float(request.POST['PVU'])
                    except:
                        logging.info("Le prix de vente unitaire doit etre un nombre")
                        return JsonResponse({'message': "Le prix de vente unitaire doit etre un nombre"}, status=510)
                else:
                    logging.info("Le champ PVU est obligatoire")
                    return JsonResponse({'message': "Le champ PVU est obligatoire"}, status=510)
                
                if 'PVG' in request.POST.keys() and  request.POST['PVG']:
                    try:
                        PVG=float(request.POST['PVG'])
                    except Exception as e:
                        print(e)
                        return JsonResponse({'message': "Le prix de vente en gros doit etre un nombre"}, status=510)
                else:
                    logging.info("Le champ PVG est obligatoire")
                    return JsonResponse({'message': "Le champ PVG est obligatoire"}, status=510)
                
                
                if nom_article == '':
                    print("Vous devez donner un nom à l'article")
                    return JsonResponse({'message': "Vous devez donner un nom à l'article"}, status=510)
                if Article.objects.filter(nom_article=nom_article).exists():
                    print("Le nom de l'article doit etre unique")
                    return JsonResponse({'message': "Le nom de l'article doit etre unique"}, status=510)
                    
                
                
                if request.POST['date_peremption'] == '' and request.POST['code_barres'] == '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        nom_article=request.POST['nom_article'].strip(), 
                        PAU=PAU,
                        PVU=PVU,
                        PVG=PVG
                    )
                elif request.POST['date_peremption'] != '' and request.POST['code_barres'] == '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        #code_barres=request.POST['code_barres'], 
                        date_peremption=request.POST['date_peremption'], 
                        nom_article=request.POST['nom_article'].strip(), 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU'],
                        PVG=request.POST['PVG']
                    )
                elif request.POST['date_peremption'] == '' and request.POST['code_barres'] != '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        code_barres=request.POST['code_barres'], 
                        #date_peremption=request.POST['date_peremption'], 
                        nom_article=request.POST['nom_article'].strip(), 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU'],
                        PVG=request.POST['PVG']
                    )
                elif request.POST['date_peremption'] != '' and request.POST['code_barres'] != '':
                    article = Article(
                        categorie=Categorie.objects.get(pk=request.POST['categorie_id']),
                        code_barres=request.POST['code_barres'], 
                        date_peremption=request.POST['date_peremption'], 
                        nom_article=request.POST['nom_article'].strip(), 
                        PAU=request.POST['PAU'], 
                        PVU=request.POST['PVU'],
                        PVG=request.POST['PVG']
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
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                article=Article.objects.get(pk = article_id)
                
                article.categorie = Categorie.objects.get(pk=request.POST['categorie_id'])
                article.nom_article = request.POST['nom_article'].strip()
                article.PAU = request.POST['PAU']
                article.PVU = request.POST['PVU']
                article.PVG = request.POST['PVG']
                
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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
            article=Article.objects.get(pk = article_id)
            article.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def ctrl_article(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/ctrl_article.html', {'liste_articles': liste_articles})
