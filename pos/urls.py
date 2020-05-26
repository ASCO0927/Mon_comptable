from django.urls import path
from . import views


app_name = 'pos'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:user_id>/vente/', views.vente, name='vente'),
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
    path('<int:user_id>/controle/avarie/', views.avarie, name='avarie'),
    path('<int:user_id>/mod/article/<int:article_id>', views.mod_article, name='mod_article'),
    path('<int:user_id>/sup/article/<int:article_id>', views.sup_article, name='sup_article'),
    path('<int:user_id>/mod/categorie/<int:categorie_id>', views.mod_categorie, name='mod_categorie'),
    path('<int:user_id>/sup/categorie/<int:categorie_id>', views.sup_categorie, name='sup_categorie'),
    path('<int:user_id>/mod/entree/<int:entree_id>', views.mod_entree, name='mod_entree'),
    path('<int:user_id>/sup/entree/<int:entree_id>', views.sup_entree, name='sup_entree'),
]
