from django.urls import path
from pos.views import views, fournisseurs, remboursements, sorties, arret_compte

from django.views.generic.base import RedirectView


app_name = 'pos'
urlpatterns = [
    path('', RedirectView.as_view(url='login/')),

    #DEBUT REMBOURSEMENT
    path('remboursements/', remboursements.remboursement_list, name='remboursement_list'),
    path('remboursement/new/', remboursements.remboursement_new, name='remboursement_new'),
    path('remboursement/<int:pk>/', remboursements.remboursement_detail, name='remboursement_detail'),
    path('remboursement/<int:pk>/edit/', remboursements.remboursement_edit, name='remboursement_edit'),
    path('remboursement/<int:pk>/delete/', remboursements.remboursement_delete, name='remboursement_delete'),
    #FIN REMBOURSEMENT

    #DEBUT FOURNISSEUR
    path('fournisseurs/', fournisseurs.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/<int:pk>/', fournisseurs.fournisseur_detail, name='fournisseur_detail'),
    path('fournisseurs/new/', fournisseurs.fournisseur_new, name='fournisseur_new'),
    path('fournisseurs/<int:pk>/edit/', fournisseurs.fournisseur_edit, name='fournisseur_edit'),
    path('fournisseurs/<int:pk>/delete/', fournisseurs.fournisseur_delete, name='fournisseur_delete'),
    #FIN FOURNISSEUR

    #DEBUT VENTE
    path('<int:user_id>/modifier_vente/', views.modifier_vente, name='modifier_vente'),
    path('vente/', views.vente, name='vente'),
    path('vente_articles/data/', views.ArticleDataTableView.as_view(), name='vente_articles_data'),
    path('<int:user_id>/annuler_vente/', views.annuler_vente, name='annuler_vente'),
    #FIN VENTE

    #DEBUT ORANGE MONEY
    path('<int:user_id>/controle/depot_caisse_orange_money/', views.depot_caisse_orange_money, name='depot_caisse_orange_money'),
    path('<int:user_id>/controle/collecte_caisse_orange_money/', views.collecte_caisse_orange_money, name='collecte_caisse_orange_money'),
    #FIN ORANGE MONEY

    #DEBUT STOCK
    path('get_stock_value/', views.get_stock_value, name='get_stock_value'),
    path('<int:user_id>/controle/stock/', views.ctrl_stock, name='ctrl_stock'),
    path('stock/data/', views.StockJson.as_view(), name='stock_data'),
    #FIN STOCK

    #DEBUT ARTICLE
    path('article/<str:barcode>/', views.ArticleByBarcodeView.as_view(), name='article_by_barcode'),
    path('article_by_article_name/<str:nom_article>/', views.ArticleByNomArticleView.as_view(), name='article_by_nom_artcle'),

    path('article_data/', views.ArticleJson.as_view(), name='article_data'),
    path('mod/article/<int:article_id>', views.mod_article, name='mod_article'),
    path('<int:user_id>/sup/article/<int:article_id>', views.sup_article, name='sup_article'),
    #FIN ARTICLE

    #DEBUT SORTIES
    path('liste_sorties/', sorties.liste_sorties_data, name='liste_sorties'),#modif lompo
    path('liste_sorties_template_view/<int:arret_pk>', sorties.liste_sorties_template_view, name='liste_sorties_template_view'),#modif lompo
    path('sorties/<int:arret_pk>/data/', sorties.SortieListJson.as_view(), name='sorties_list_data'),#modif lompo
    #FIN SORTIE

    #DEBUT ARRET COMPTE
    path('arrets_comptes/', arret_compte.arret_compte, name='arret_compte'),#modif lompo
    #FIN ARRET COMPTE

    path('<int:user_id>/generer_proforma/', views.generer_proforma, name='generer_proforma'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    path('avaries/data/', views.AvarieJson.as_view(), name='avaries_data'),
    path('<int:user_id>/nouvelle_avarie/', views.nouvelle_avarie, name='nouvelle_avarie'),
    path('<int:user_id>/avaries/', views.liste_produits_avaries, name='liste_produits_avaries'),

    
    path('<int:user_id>/controle/le_point/', views.le_point, name='le_point'),
    
    path('<int:user_id>/controle/vente/', views.ctrl_vente, name='ctrl_vente'),

    path('<int:user_id>/controle/caisse/', views.ctrl_caisse, name='ctrl_caisse'),
    

    path('<int:user_id>/controle/entrees/', views.ctrl_entree, name='ctrl_entree'),

    path('<int:user_id>/controle/articles/', views.ctrl_article, name='ctrl_article'),

    path('<int:user_id>/controle/categories/', views.ctrl_categorie, name='ctrl_categorie'),
    path('<int:user_id>/controle/nouvelle_entree/', views.nouvelle_entree, name='nouvelle_entree'),
    path('<int:user_id>/controle/nouvelle_article/', views.nouvelle_article, name='nouvelle_article'),
    path('<int:user_id>/controle/nouvelle_categorie/', views.nouvelle_categorie, name='nouvelle_categorie'),
    path('<int:user_id>/controle/depot_petite_monnaie/', views.depot_petite_monnaie, name='depot_petite_monnaie'),
    path('<int:user_id>/controle/collecte_caisse/', views.collecte_caisse, name='collecte_caisse'),
    
    
    path('mod/categorie/<int:categorie_id>', views.mod_categorie, name='mod_categorie'),
    path('<int:user_id>/sup/categorie/<int:categorie_id>', views.sup_categorie, name='sup_categorie'),
    path('mod/entree/<int:entree_id>', views.mod_entree, name='mod_entree'),
    path('<int:user_id>/sup/entree/<int:entree_id>', views.sup_entree, name='sup_entree'),

    path('lst/client/', views.list_clients, name='lst_client'),
    path('nvo/client/', views.nouveau_client, name='nouveau_client'),
    path('mod/client/<int:client_id>', views.mod_client, name='mod_client'),
    path('sup/client/<int:client_id>', views.sup_client, name='sup_client'),

    path('lst/transactions/<int:client_id>', views.lst_transactions_client, name='lst_transactions_client'),

    path('avance/<int:client_id>', views.depot_client, name='avance_client'),
]
