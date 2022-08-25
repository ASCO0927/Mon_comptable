from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from ..models import (Article, Avarie)
from .utils import quantite_en_stock

def nouvelle_avarie(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_articles = Article.objects.all()
            return render(request, 'pos/avaries/nouvelle_avarie.html', {'liste_articles': liste_articles})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                
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

