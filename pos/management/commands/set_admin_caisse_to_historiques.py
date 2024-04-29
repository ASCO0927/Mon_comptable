from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pos.models import HistoriqueDepotRamassageCaisse, Caisse


class Command(BaseCommand):
    help = 'Update null Caisse to admin user for all HistoriqueDepotRamassageCaisse objects'

    def handle(self, *args, **kwargs):
        # Get the user named 'admin'
        admin_user = User.objects.get(username='admin')
        # Get the Caisse for 'admin'
        admin_caisse = Caisse.objects.get(user=admin_user)
        # Get all HistoriqueDepotRamassageCaisse objects with null Caisse
        historiques = HistoriqueDepotRamassageCaisse.objects.filter(caisse__isnull=True)
        # Update the Caisse to admin's Caisse for all those objects
        historiques.update(caisse=admin_caisse)
        self.stdout.write(self.style.SUCCESS('Successfully updated Caisse for all HistoriqueDepotRamassageCaisse objects'))


