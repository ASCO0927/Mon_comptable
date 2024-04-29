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

from ..models import (Article, Entree,Fournisseur)

def ctrl_entree(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            date_filtre = request.GET.get('date_filtre')

            if date_filtre is None:
                date_filtre = timezone.now().date()
            else:
                date_filtre = datetime.strptime(date_filtre, '%Y-%m-%d').date()

            day_min = datetime.combine(date_filtre, datetime.min.time())
            day_max = datetime.combine(date_filtre, datetime.max.time())

            liste_entrees = []
            for entree in Entree.objects.filter(date_entree__range=(day_min, day_max)).order_by('-id'):
                jour = entree.date_entree.strftime("%d/%m/%Y")
                heure = entree.date_entree.strftime("%H:%M")
                liste_entrees.append({'id': entree.id, 'jour': jour, 'heure': heure, 'article': entree.article.nom_article, 'quantite': entree.quantite, 'reste_a_payer': entree.reste_a_payer, 'fournisseur': entree.fournisseur})

            #liste_entrees.reverse()
            return render(request, 'pos/entrees/ctrl_entree.html', {'liste_entrees': liste_entrees, 'today': date_filtre})


def nouvelle_entree(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            liste_fournisseurs = Fournisseur.objects.all()  # ajouter les fournisseurs
            return render(request, 'pos/entrees/nouvelle_entree.html', {'liste_articles': liste_articles, 'liste_fournisseurs': liste_fournisseurs})  # passer les fournisseurs au contexte
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                # Récupérer le fournisseur par l'id, l'objet fournisseur est null si aucun fournisseur n'est sélectionné
                fournisseur = Fournisseur.objects.get(pk=request.POST['fournisseur_id']) if request.POST['fournisseur_id'] else None 
                paye = request.POST['paye'] == 'true'  # Transforme le string en boolean
                entree = Entree(article=Article.objects.get(pk=request.POST['article_id']), 
                                quantite=request.POST['quantite'], 
                                date_entree=timezone.now(), 
                                fournisseur=fournisseur, 
                                paye=paye) # passer le fournisseur et paye à Entree
                entree.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_entree(request, entree_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            entree=Entree.objects.get(pk = entree_id)
            return render(request, 'pos/entrees/mod_entree.html', {'liste_articles': liste_articles, 'entree': entree})
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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
            entree=Entree.objects.get(pk = entree_id)
            entree.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)
