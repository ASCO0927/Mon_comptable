from django.core.management.base import BaseCommand, CommandError
from pos.models import (Article, Categorie, Entree)
from django.utils import timezone
from faker import Faker
fake = Faker()

class Command(BaseCommand):
    help = 'ajouter des articles dans la base de donnee pour test'
    '''
    def add_arguments(self, parser):
        parser.add_argument('poll_ids', nargs='+', type=int)
    '''
    def handle(self, *args, **options):
        categorie_id = Categorie.objects.all()[0].id
        for i in range(100):
            article = Article(
                categorie=Categorie.objects.get(pk=categorie_id),
                nom_article=fake.name(),
                PAU=1000,
                PVU=1500,
                PVG=1200
            )
            article.save()

            entree = Entree(article=article, quantite=100, date_entree=timezone.now())
            entree.save()

            self.stdout.write(self.style.SUCCESS('Successfully created article "%s"' % article.nom_article))
