import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from pos.models import Article, Categorie, Entree

from pos.views.utils import catalogue_et_stock
from django.conf import settings
import csv
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Inport stock from stock.csv'

    def handle(self, *args, **kwargs):
        file_name = "stock.csv"
        input_file = os.path.join(settings.BASE_DIR, file_name)

        if len(Categorie.objects.all()):
            with open(input_file, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                categorie_id = Categorie.objects.all()[0].id
                for row in csv_reader:
                    code_barres = row.get("code_barres", None)
                    #nom_categorie = row.get("categorie", '')
                    nom_article = row.get("nom_article", '')
                    PAU = row.get("PAU", 0)
                    PVU = row.get("PVU", 0)
                    PVG = row.get("PVG", 0)
                    en_stock = row.get("en_stock", '')
                    date_peremption = row.get("date_peremption", None)

                    if code_barres:
                        article = Article(
                            code_barres=code_barres,
                            categorie=Categorie.objects.get(pk=categorie_id),
                            nom_article=nom_article,
                            PAU=float(PAU),
                            PVU=float(PVU),
                            PVG=float(PVG),
                            date_peremption = None if date_peremption is None or len(date_peremption) == 0 else datetime.strptime(date_peremption.split(' ')[0], '%Y-%m-%d')
                        )
                    else:
                        article = Article(
                            categorie=Categorie.objects.get(pk=categorie_id),
                            nom_article=nom_article,
                            PAU=float(PAU),
                            PVU=float(PVU),
                            PVG=float(PVG),
                            date_peremption = None if date_peremption is None or len(date_peremption) == 0 else datetime.strptime(date_peremption.split(' ')[0], '%Y-%m-%d')
                        )
                    article.save()

                    entree = Entree(article=article, quantite=int(en_stock), date_entree=timezone.now())
                    entree.save()

                    self.stdout.write(self.style.SUCCESS('Successfully created article "%s"' % article.nom_article))
        else:
            print('Vous devez créer au moins une catégorie de produit avant d importer')
