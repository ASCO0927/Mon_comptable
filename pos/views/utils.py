from django.utils import timezone
from django.db.models import Sum

def catalogue_et_stock():
    from ..models import (Article, Entree)

    articles_en_catalogue = Article.objects.all()
    liste_articles_en_catalogue = []

    for article in articles_en_catalogue:
        entree=Entree.objects.filter(article = article.id)

        if len(entree):
            id_derniere_entree = entree[len(entree)-1].pk
        else:
            entree = Entree(article=article, quantite=0, date_entree=timezone.now())
            entree.save()
            id_derniere_entree = entree.id

        en_stock = quantite_en_stock(article)
        couleur_stock = ""
        if en_stock < 15 and en_stock != 0:
            couleur_stock = "yellow"
        elif en_stock < 1:
            couleur_stock = "red"
        
        couleur_date_peremption = ""
        if article.article_est_perime():
            couleur_date_peremption = "red"
        elif article.perime_dans_moins_de(30*3):
            couleur_date_peremption = "orange"

        liste_articles_en_catalogue.append({"id": article.id, "code_barres": article.code_barres, "categorie": article.categorie, "nom_article": article.nom_article, "PAU": article.PAU, "PVU": article.PVU, "PVG": article.PVG, "en_stock": en_stock, "id_derniere_entree": id_derniere_entree, "couleur_stock": couleur_stock, "couleur_date_peremption": couleur_date_peremption, "date_peremption": article.date_peremption,})

    return liste_articles_en_catalogue
        

def quantite_en_stock(article_recherche):
    from ..models import (Avarie, Entree, Sortie)

    liste_sorties = Sortie.objects.filter(article=article_recherche)
    liste_avaries = Avarie.objects.filter(article=article_recherche)
    liste_entrees = Entree.objects.filter(article=article_recherche)
    total_sortie = 0
    total_avarie = 0
    total_entree = 0

    for sortie in liste_sorties:
        total_sortie = total_sortie + sortie.quantite
    
    for avarie in liste_avaries:
        total_avarie = total_avarie + avarie.quantite

    for entree in liste_entrees:
        total_entree = total_entree + entree.quantite
    
    return total_entree - total_sortie - total_avarie
