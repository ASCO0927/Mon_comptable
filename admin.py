from django.contrib import admin
from .models import *

class CategorieAdmin(admin.ModelAdmin):
    pass

class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['nom_article']
    list_display = ('nom_article', 'code_barres', 'date_peremption', 'PAU', 'PVU', 'categorie')
    

class EntreeAdmin(admin.ModelAdmin):
    search_fields = ['article__nom_article']
    list_display = ('article', 'quantite', 'date_entree')
    date_hierarchy = 'date_entree'

class AvarieAdmin(admin.ModelAdmin):
    search_fields = ['article__nom_article']
    list_display = ('article', 'quantite', 'date_avarie')
    date_hierarchy = 'date_avarie'

class SortieAdmin(admin.ModelAdmin):
    search_fields = ['article__nom_article']
    list_display = ('article', 'quantite', 'numero_vente')

class VenteAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_vente'


admin.site.register(Parametre)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Entree, EntreeAdmin)
admin.site.register(Avarie, AvarieAdmin)
admin.site.register(Sortie, SortieAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(ArretOperation)
admin.site.register(Controle)
admin.site.register(Caisse)
admin.site.register(HistoriqueDepotRamassageCaisse)
admin.site.register(CompteOrangeMoney)
admin.site.register(HistoriqueDepotRamassageCompteOrangeMoney)
admin.site.register(Fournisseur)
admin.site.register(RemboursementFournisseur)
admin.site.register(ArretCompte)