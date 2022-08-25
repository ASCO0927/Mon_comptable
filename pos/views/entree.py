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

def nouvelle_entree(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/nouvelle_entree.html', {'liste_articles': liste_articles})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                entree = Entree(article=Article.objects.get(pk = request.POST['article_id']), quantite=request.POST['quantite'], date_entree=timezone.now())
                entree.save()
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
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
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
