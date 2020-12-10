from django.urls import path
from . import views

'''
from django.utils import timezone
from .models import Article, Vente, Sortie, Avarie, Entree, Controle, Categorie, Coupures, OperationsCaisse
from datetime import datetime


def batch_creation(nom_article, quantite, PVU):
    article = Article(categorie=Categorie.objects.get(nom_categorie='Default'), nom_article=nom_article, PAU=0, PVU=PVU)
    article.save()
    print("article {} creee".format(article.nom_article))

    entree = Entree(article=article, quantite=quantite, date_entree=timezone.now())
    entree.save()
    print('nouvelle entree : {}, {}'.format(article.nom_article, entree.quantite))

article_list = [
    ['savon dure', 3, 1250],
    ['hollywood', 10, 100],
    ['biscuit lerrai', 23, 150],
    ['biscuit bless', 34, 50],
    ['gateau nada', 15, 100],
    ['bobon lollipop', 12, 50],
    ['choc cup', 13, 50],
    ['bonbon jew', 11, 50],
    ['bonbon boite boisson', 12, 50],
    ['cirage kiui', 7, 500],
    ['brosse a cirage', 5, 400],
    ['brosse a cirage aterma', 7, 400],
    ['bougie', 22, 50],
    ['allumette yaya', 109, 25],
    ['allumette the king', 4, 750],
    ['allumette silver', 3, 250],
    ['brique', 58, 50],
    ['pile nakko petit', 14, 50],
    ['pile naweather gros', 17, 50],
    ['une minute pommade', 7, 500],
    ['une minute savon', 12, 500],
    ['bic bleu', 20, 100],
    ['craie', 149, 12.5],
    ['cahier de 200', 4, 300],
    ['cahier de 100', 10, 150],
    ['enveloppe A3', 0, 100],
    ['enveloppe A4', 23, 50],
    ['enveloppe A5', 6, 25],
    ['feuille de demande', 0, 25],
    ['chiffon', 9, 100],
    ['rasoir bic', 15, 200],
    ['serviette de table', 12, 500],
    ['riz de 5 kg', 1, 4500],
    ['avovita creme gros', 1, 1250],
    ['avovita creme petit', 2, 500],
    ['pommade day by day', 1, 750],
    ['carro paa princess', 2, 1000],
    ['savon liquide artize', 3, 800],
    ['pommade kari derme', 2, 750],
    ['bome de nerfs', 3, 500],
    ['wild cat menthelanto', 3, 500],
    ['base menthol', 1, 500],
    ['pommade katerina', 1, 600],
    ['afro star', 1, 500],
    ['vaseline petroleum', 2, 400],
    ['defrisant soft hair petit', 2, 500],
    ['defrisant soft hair gros', 0, 1000],
    ['glycerine sonia', 1, 300],
    ['miss laureta', 4, 200],
    ['labello leure', 3, 650],
    ['total relax anti moustique', 12, 800],
    ['rambo insecticide', 1, 1000],
    ['insecticide durable efficiency', 1, 1000],
    ['insecticide powerful', 24, 1000],
    ['insecticide fatalo aerosol', 24, 1000],
    ['verre jettable gros', 2, 1750],
    ['verre jettable petit', 3, 750],
    ['assiette', 1, 2250],
    ['carte de jeu lion', 8, 200],
    ['rafined', 50, 50],
    ['cirage black lude', 12, 500],
    ['arachide salé', 10, 100],
    ['arache sucre', 12, 100],
    ['mangue séchée', 5, 100],
    ['coco séché', 4, 100],
    ['poudre de colorant boisson', 39, 50],
    ['arome 3 lion', 7, 250],
    ['gingimbre séché', 4, 100],
    ['huile savor 3l', 0, 3000],
    ['huile savor 1l', 0, 1100],
    ['gateau boule de neige', 7, 100],
    ['gateau sucre 25', 29, 29],
    ['gateau sucre 50', 6, 100],
    ['datte', 9, 100],
    ['lait frais nono', 18, 300],
    ['lait sucre nono', 18, 300],
    ['fanta gros', 4, 1000],
    ['fanta 400', 22, 400],
    ['fanta 300', 00, 300],
    ['fanta 200', 63, 200],
    ['coca gros', 10, 1000],
    ['coca 400', 34, 400],
    ['coca 300', 0, 300],
    ['coca 200', 31, 200],
    ['tonic 400', 13, 400],
    ['tonic 300', 0, 300],
    ['tonic 200', 20, 200],
    ['sprite gros', 0, 1000],
    ['sprite 400', 14, 400],
    ['sprite 300', 8, 300],
    ['sprite 200', 25, 200],
    ['moca cafe 400', 12, 400],
    ['moca cafe 300', 0, 300],
    ['moca cafe 200', 0, 200],
    ['xxl 600', 13, 600],
    ['planet anana 200', 22, 200],
    ['planet coca 200', 15, 200],
    ['planet tamarin 200', 12, 200],
    ['planet xxplus', 1, 350],
    ['lafi eau gros', 33, 500],
    ['vimma eau gros', 26, 400],
    ['lafi petit', 14, 250],
    ['vimma petit', 24, 200],
    ['jus etoile', 13, 200],
    ['fruity 150', 35, 150],
    ['kolipo 250', 48, 250],
    ['baradji', 0, 100],
    ['eau ideal', 23, 500],
    ['riz 25kg trois soeur', 1, 12000],
    ['riz 25kg ginny', 1, 10000],
    ['riz 50kg 19500', 0, 19500],
    ['riz 50kg 23000', 0, 23000],
    ['riz 50kg 20500', 0, 20500],
    ['lipton ginny', 2, 500],
    ['thé gingimbre', 4, 1750],
    ['papyon bonbon', 55, 25],
    ['koffykop', 207, 12.5],
    ['lave vitre', 2, 1500],
    ['poudre familia', 3, 1000],
    ['birthday petard petit', 6, 1500],
    ['birthday petard moyen', 6, 2000],
    ['birthday petard gros', 6, 3000],
    ['cole pour plaie', 99, 25],
    ['pile topsaho gros', 8, 125],
    ['rasoir dorco', 5, 200],
    ['kit jettable', 0, 5500],
    ['moustiqo superconfo', 50, 300],
    ['menthorub', 60, 50],
    ['croquette arachide', 3, 100],
    ['huile aya 3l', 0, 3000],
]

for article in article_list:
    batch_creation(article[0], article[1], article[2])
'''


app_name = 'pos'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:user_id>/vente/', views.vente, name='vente'),


    path('<int:user_id>/nouvelle_avarie/', views.nouvelle_avarie, name='nouvelle_avarie'),
    path('<int:user_id>/avaries/', views.liste_produits_avaries, name='liste_produits_avaries'),

    
    path('<int:user_id>/controle/le_point/', views.le_point, name='le_point'),
    path('<int:user_id>/controle/vente/', views.ctrl_vente, name='ctrl_vente'),
    path('<int:user_id>/controle/caisse/', views.ctrl_caisse, name='ctrl_caisse'),
    path('<int:user_id>/controle/stock/', views.ctrl_stock, name='ctrl_stock'),
    path('<int:user_id>/controle/entrees/', views.ctrl_entree, name='ctrl_entree'),
    path('<int:user_id>/controle/articles/', views.ctrl_article, name='ctrl_article'),
    path('<int:user_id>/controle/categories/', views.ctrl_categorie, name='ctrl_categorie'),
    path('<int:user_id>/controle/nouvelle_entree/', views.nouvelle_entree, name='nouvelle_entree'),
    path('<int:user_id>/controle/nouvelle_article/', views.nouvelle_article, name='nouvelle_article'),
    path('<int:user_id>/controle/nouvelle_categorie/', views.nouvelle_categorie, name='nouvelle_categorie'),
    path('<int:user_id>/controle/depot_petite_monnaie/', views.depot_petite_monnaie, name='depot_petite_monnaie'),
    path('<int:user_id>/controle/collecte_caisse/', views.collecte_caisse, name='collecte_caisse'),\
    
    path('<int:user_id>/mod/article/<int:article_id>', views.mod_article, name='mod_article'),
    path('<int:user_id>/sup/article/<int:article_id>', views.sup_article, name='sup_article'),
    path('<int:user_id>/mod/categorie/<int:categorie_id>', views.mod_categorie, name='mod_categorie'),
    path('<int:user_id>/sup/categorie/<int:categorie_id>', views.sup_categorie, name='sup_categorie'),
    path('<int:user_id>/mod/entree/<int:entree_id>', views.mod_entree, name='mod_entree'),
    path('<int:user_id>/sup/entree/<int:entree_id>', views.sup_entree, name='sup_entree'),

    path('lst/client/', views.list_clients, name='lst_client'),
    path('nvo/client/', views.nouveau_client, name='nouveau_client'),
    path('mod/client/<int:client_id>', views.mod_client, name='mod_client'),
    path('sup/client/<int:client_id>', views.sup_client, name='sup_client'),

    path('lst/transactions/<int:client_id>', views.lst_transactions_client, name='lst_transactions_client'),

    path('avance/<int:client_id>', views.depot_client, name='avance_client'),

]
