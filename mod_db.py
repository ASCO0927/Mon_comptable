import os
from pos.models import Article, Avarie, Caisse, Categorie, Client, Controle, Depot, Entree, HistoriqueDepotRamassageCaisse, Sortie, HistoriqueTransactionsClient, Vente, CompteOrangeMoney, HistoriqueDepotRamassageCompteOrangeMoney



#python manage.py shell

'''
def traiter_doublons():
    liste_nom_articles = []
    for article in Article.objects.all():
        if article.nom_article in liste_nom_articles:
            article.nom_article = f"{article.nom_article} copie_{article.id}"
            article.save()
            liste_nom_articles.append(article.nom_article)
            print(f'mise a jour {article.nom_article}')
        else:
            liste_nom_articles.append(article.nom_article)

def maj_prix_vente_sortie():
    for sortie in Sortie.objects.all():
        if sortie.prix_vente_article == 0:
            sortie.prix_vente_article = sortie.article.PVU
            sortie.save()
            print(sortie)
            
maj_prix_vente_sortie()
#traiter_doublons()
'''
