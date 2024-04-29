import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from ..models import (Article, Categorie, Entree)
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.views import View
from pos.models import Article
from django.shortcuts import get_object_or_404

class ArticleByBarcodeView(View):
    def get(self, request, *args, **kwargs):
        barcode = kwargs.get('barcode')
        article = get_object_or_404(Article, code_barres=barcode)
        data = {
            'nom_article': article.nom_article,
            'en_stock': article.en_stock,
            'PVU': str(article.PVU), # converted to string as Decimal is not JSON serializable
            # include any other fields you need
        }
        return JsonResponse(data)

class ArticleByNomArticleView(View):
    def get(self, request, *args, **kwargs):
        nom_article = kwargs.get('nom_article')
        article = get_object_or_404(Article, nom_article=nom_article)
        data = {
            'nom_article': article.nom_article,
            'en_stock': article.en_stock,
            'PVU': str(article.PVU), # converted to string as Decimal is not JSON serializable
            'PVG': str(article.PVG),
            # include any other fields you need
        }
        return JsonResponse(data)

def nouvelle_article(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            return render(request, 'pos/articles/nouvelle_article.html', {'liste_categories': liste_categories})
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


def mod_article(request, article_id, *args, **kwargs):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            liste_categories = Categorie.objects.all()
            article=Article.objects.get(pk = article_id)
            return render(request, 'pos/articles/mod_article.html', {'liste_categories': liste_categories, 'article': article})
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


class ArticleJson(BaseDatatableView):
    model = Article
    columns = ['categorie', 'nom_article', 'PAU', 'PVU', 'marge_detail', 'PVG', 'marge_gros', 'code_barres']

    def render_column(self, row, column):
        if column == 'categorie':
            return str(row.categorie)
        else:
            return super(ArticleJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(nom_article__icontains=sSearch) | 
                           Q(PAU__icontains=sSearch) |
                           Q(PVU__icontains=sSearch) |
                           Q(PVG__icontains=sSearch) |
                           Q(code_barres__icontains=sSearch) |
                           Q(categorie__nom_categorie__icontains=sSearch))
        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            PVG = item.PVG or 0
            json_data.append([
                str(item.categorie),
                item.nom_article,
                float(item.PAU),
                float(item.PVU),
                float(item.PVU - item.PAU),  # Marge Detail
                float(PVG),
                float(PVG - item.PAU),  # Marge Gros
                item.code_barres,
                item.id,
            ])
        return json_data
    
    def ordering(self, qs):
        order = self._querydict.get('order[0][column]', None)
        dir = self._querydict.get('order[0][dir]', None)

        if order is not None:
            column_number = int(order)
            column = self.columns[column_number]

            if column == 'marge_detail':
                # If the column is 'marge_detail', order by PVU - PAU
                if dir == 'asc':
                    return sorted(qs, key=lambda x: x.PVU - x.PAU)
                else:
                    return sorted(qs, key=lambda x: x.PVU - x.PAU, reverse=True)
            elif column == 'marge_gros':
                # If the column is 'marge_gros', order by PVG - PAU
                if dir == 'asc':
                    return sorted(qs, key=lambda x: x.PVG - x.PAU)
                else:
                    return sorted(qs, key=lambda x: x.PVG - x.PAU, reverse=True)
            else:
                return super(ArticleJson, self).ordering(qs)
        else:
            return qs


def ctrl_article(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/articles/ctrl_article.html')
