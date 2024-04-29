from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q

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


class AvarieJson(BaseDatatableView):
    model = Avarie
    columns = ['article', 'quantite', 'date_avarie',]

    def render_column(self, row, column):
        if column == 'article':
            return str(row.article.nom_article)
        else:
            return super(AvarieJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(article__nom_article__icontains=sSearch) | 
                           Q(quantite__icontains=sSearch) |
                           Q(date_avarie__icontains=sSearch))
        return qs


def liste_produits_avaries(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/avaries/liste_produits_avaries.html')

