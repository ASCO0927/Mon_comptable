from ast import Try
import json
from django.db.models import Q
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from datetime import datetime
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ..models import (Article, Caisse, Client,
                     CompteOrangeMoney,
                     HistoriqueTransactionsClient, Sortie, Vente, Entree, Avarie)

from ..recus import enregistrer_recu_type1, enregistrer_recu_type2
from .utils import *
from django.views import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Sum, Subquery, OuterRef
from django.shortcuts import render, get_object_or_404, redirect


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
        vente = get_object_or_404(Vente, id=id_vente)
        vente.delete()
        vente(request, user_id)


def annuler_vente(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            vente = get_object_or_404(Vente, id=request.POST.get('id'))
            vente.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'})



#-------------------DEBUT VENTE-----------------

def get_money_val(post, key):
    if key in post and post[key].isnumeric():
        return post[key]
    else:
        return 0


def get_first_or_create(model, defaults=None):
    objects = model.objects.all()
    if len(objects) == 0:
        new_object = model(**defaults) if defaults else model()
        new_object.save()  # Save the newly created object
        return new_object
    return objects[0]


def process_sale_articles(sale_articles, vente):
    montant_vente = 0
    for article in json.loads(sale_articles):
        article_a_vendre = Article.objects.get(nom_article = article["article"])
        quantite_a_vendre = int(article["quantite"])
        prix_article = float(article["prix"])

        # Si vente est None, nous vérifions seulement le stock
        if vente is None:
            montant_vente += quantite_a_vendre * prix_article
            if article_a_vendre.en_stock < quantite_a_vendre:
                return {'error': 'Not enough stock for article {}'.format(article_a_vendre.nom_article)}

        # Si vente n'est pas None, nous effectuons la vente
        else:
            montant_vente += quantite_a_vendre * prix_article
            sortie = Sortie(article=article_a_vendre, quantite=quantite_a_vendre, prix_vente_article=float(prix_article), numero_vente=vente)
            sortie.save()

    return montant_vente


def generate_invoice(type_recu, sale_articles, montant_vente, client, montant_encaisse, monnaie_rendue):
    if type_recu == 1:
        enregistrer_recu_type1(sale_articles, client)
    else:
        if int(montant_encaisse) == 0:
            enregistrer_recu_type2(sale_articles, montant_vente, monnaie_rendue)
        else:
            enregistrer_recu_type2(sale_articles, montant_encaisse, monnaie_rendue)


def check_date_and_auth(request):
    if date.today() > date(2033, 8, 15) or not request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    return None


def handle_vente_get_request(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
        caisse = Caisse.objects.get(user=request.user)
        compte_orange_money = get_first_or_create(CompteOrangeMoney, defaults={'montant': 0})
        return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant, 'orange_money': compte_orange_money.montant}, status=200)
    else:
        liste_articles_en_catalogue = []
        liste_clients = Client.objects.all()
        context = {'liste_articles_en_catalogue': liste_articles_en_catalogue, 'liste_clients': liste_clients}
        return render(request, 'pos/vente/vente.html', context)


def handle_vente_post_request(request):
    sale_articles = request.POST.get('liste_articles_a_vendre', [])
    monnaie_rendue = get_money_val(request.POST, 'monnaie_rendue')
    montant_encaisse = get_money_val(request.POST, 'montant_encaisse')

    client_id = request.POST.get('client_id')
    client = Client.objects.get(id=client_id) if client_id != '' else None

    payment_mode = request.POST.get('mode_paiement')
    now = timezone.now()

    # Vérification des stocks avant de créer la vente
    montant_vente = process_sale_articles(sale_articles, None)
    if isinstance(montant_vente, dict) and "error" in montant_vente:
        return JsonResponse(montant_vente, status=400)

    # Création de la vente après la vérification des stocks
    vente = Vente(vendeur=request.user, montant_vente=montant_vente, montant_encaisse=montant_encaisse, monnaie_rendue=monnaie_rendue, date_vente=now, client=client, payment_mode=payment_mode)
    vente.save()

    # Création des articles de vente après la création de la vente
    montant_vente = process_sale_articles(sale_articles, vente)

    generate_invoice(1, sale_articles, montant_vente, client, montant_encaisse, monnaie_rendue)
    
    return JsonResponse({
        "vente_id": vente.id,
        "date_vente": now.strftime('%Y-%m-%d %H:%M:%S'),
        'caisse': Caisse.objects.get(user=request.user).montant, 
        'orange_money': CompteOrangeMoney.objects.first().montant
    })


def vente(request):
    response = check_date_and_auth(request)
    if response:
        return response

    if request.method == 'POST':
        return handle_vente_post_request(request)
    else:
        return handle_vente_get_request(request)

#-------------------FIN VENTE-----------------


def ctrl_vente(request, user_id):
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

            ventes = Vente.objects.filter(date_vente__range=(day_min, day_max)).order_by('-id')
            liste_ventes = [{'id': vente.id, 'jour': vente.date_vente.strftime("%d/%m/%Y"), 'heure': vente.date_vente.strftime("%H:%M")} for vente in ventes]

            return render(request, 'pos/vente/ctrl_vente.html', {'liste_ventes': liste_ventes, 'today': date_filtre})
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

class ArticleDataTableView(BaseDatatableView):

    model = Article
    columns = ['nom_article', 'en_stock', 'PVU', 'PVG', 'code_barres', 'date_peremption']

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.annotate(
                str_PAU=Cast('PAU', CharField(max_length=255)),
                str_PVU=Cast('PVU', CharField(max_length=255)),
                str_PVG=Cast('PVG', CharField(max_length=255)),
                str_date_peremption=Cast('date_peremption', CharField(max_length=255))
            ).filter(
                Q(categorie__nom_categorie__icontains=search) |
                Q(nom_article__icontains=search) |
                Q(code_barres__icontains=search) |
                Q(str_date_peremption__icontains=search) |
                Q(str_PAU__icontains=search) |
                Q(str_PVU__icontains=search) |
                Q(str_PVG__icontains=search)
            )

        return qs
    
    def ordering(self, qs):
        order = self._querydict.get('order[0][dir]', 'asc')
        column = self._querydict.get('order[0][column]', '0')
        column_name = self.columns[int(column)]
        
        if column_name == 'en_stock':
            new_qs = qs.annotate(
                total_stock=Subquery(
                    Entree.objects.filter(article=OuterRef('pk')).annotate(total_entree=Sum('quantite')).values('total_entree')[:1]
                ) - Subquery(
                    Sortie.objects.filter(article=OuterRef('pk')).annotate(total_sortie=Sum('quantite')).values('total_sortie')[:1]
                ) - Subquery(
                    Avarie.objects.filter(article=OuterRef('pk')).annotate(total_avarie=Sum('quantite')).values('total_avarie')[:1]
                )
            )
            if order == 'asc':
                return new_qs.order_by('total_stock')
            else:
                return new_qs.order_by('-total_stock')

        return super().ordering(qs)


    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            couleur_stock = "yellow" if item.en_stock < 15 and item.en_stock != 0 else ("red" if item.en_stock < 1 else "")
            couleur_date_peremption = "orange" if item.perime_dans_moins_de(30*3) else ("red" if item.article_est_perime() else "")
            
            json_data.append({
                "nom_article": item.nom_article,
                "en_stock": item.en_stock,
                "_stock_color": couleur_stock,
                "PVU": str(item.PVU),
                "PVG": str(item.PVG),
                "code_barres": item.code_barres,
                "date_peremption": str(item.date_peremption),
                "_date_peremption": couleur_date_peremption,
            })

        return json_data
