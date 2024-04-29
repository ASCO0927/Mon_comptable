from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from ..models import (Categorie)

def nouvelle_categorie(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/categories/nouvelle_categorie.html')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                categorie = Categorie(nom_categorie=request.POST['nom_categorie'].strip())
                categorie.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def mod_categorie(request, categorie_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            categorie=Categorie.objects.get(pk = categorie_id)
            return render(request, 'pos/categories/mod_categorie.html', {'categorie': categorie})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                categorie=Categorie.objects.get(pk = categorie_id)
                
                categorie.nom_categorie = request.POST['nom_categorie'].strip()
                
                categorie.save()
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def sup_categorie(request, user_id, categorie_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
            categorie=Categorie.objects.get(pk = categorie_id)
            categorie.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def ctrl_categorie(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            return render(request, 'pos/categories/ctrl_categorie.html', {'liste_categories': liste_categories})
