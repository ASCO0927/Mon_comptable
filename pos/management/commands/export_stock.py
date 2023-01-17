import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from pos.views.utils import catalogue_et_stock
from django.conf import settings
import csv

class Command(BaseCommand):
    help = 'Export data'

    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-o', '--output', type=str, help='file name', )

    def handle(self, *args, **kwargs):
        
        output = kwargs['output']
        liste_articles_en_catalogue = catalogue_et_stock()
        file_name = "stock.csv"
        output_file = os.path.join(settings.BASE_DIR, file_name)
        if len(liste_articles_en_catalogue):
            with open(file_name, 'w', encoding='utf8', newline='') as output_file:
                fc = csv.DictWriter(output_file, fieldnames=liste_articles_en_catalogue[0].keys(),)
                fc.writeheader()
                fc.writerows(liste_articles_en_catalogue)
            print(f'Stock exporté dans {output_file}')
        else:
            print('Stock vide: Rien à exporter!')