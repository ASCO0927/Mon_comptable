from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models import Sum, F
from pos.views.utils import quantite_en_stock
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect


class Caisse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    montant = models.IntegerField(default=0)

    def update_montant(self, amount):
        self.montant += int(amount)
        self.save()

    def __str__(self):
        return "{}, {} fcfa".format(self.user, self.montant)


class HistoriqueDepotRamassageCaisse(models.Model):
    choix_operation = models.TextChoices('choix_operation', 'depot ramassage')
    operateur = models.ForeignKey(User, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    type_operation = models.CharField(choices=choix_operation.choices, max_length=200)
    date_operation = models.DateTimeField('date encaissement')
    caisse = models.ForeignKey(Caisse, on_delete=models.CASCADE, null=True)  # Added foreign key to Caisse model

    def save(self, *args, **kwargs):
        if self.pk is None:  # if the object doesn't have an ID yet, it's a new object
            if self.type_operation == 'depot':
                self.caisse.montant += self.montant
            elif self.type_operation == 'ramassage':
                self.caisse.montant -= self.montant
            self.caisse.save()
        else:  # if the object has an ID, it's being updated
            old_historique = HistoriqueDepotRamassageCaisse.objects.get(pk=self.pk)
            # First, add the old amount back to the cashbox
            if old_historique.type_operation == 'depot':
                self.caisse.montant -= old_historique.montant
            elif old_historique.type_operation == 'ramassage':
                self.caisse.montant += old_historique.montant
            # Then subtract the new amount
            if self.type_operation == 'depot':
                self.caisse.montant += self.montant
            elif self.type_operation == 'ramassage':
                self.caisse.montant -= self.montant
            self.caisse.save()
        super(HistoriqueDepotRamassageCaisse, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.type_operation == 'depot':
            self.caisse.montant -= self.montant
        elif self.type_operation == 'ramassage':
            self.caisse.montant += self.montant
        self.caisse.save()
        super(HistoriqueDepotRamassageCaisse, self).delete(*args, **kwargs)

    def __str__(self):
        return "{}, {}, {}, {}".format(self.date_operation, self.type_operation, self.montant, self.operateur)


@receiver(post_save, sender=User)
def create_user_caisse(sender, instance, created, **kwargs):
    if created:
        Caisse.objects.create(user=instance)


class Parametre(models.Model):
    choix_recu = models.TextChoices('choix_recu', 'A4 Thermique')
    type_recu = models.CharField(choices=choix_recu.choices, max_length=200)
    afficher_le_nom_du_client_sur_le_recu = models.BooleanField(default=False, blank=True, null=True)
    afficher_le_nom_du_vendeur_sur_le_recu = models.BooleanField(default=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'type recu: {self.type_recu}, affricher nom client: {self.afficher_le_nom_du_client_sur_le_recu}, afficher nom vendeur : {self.afficher_le_nom_du_vendeur_sur_le_recu}'


#classes du client
class Client(models.Model):
    nom = models.CharField(max_length=200)
    prenoms = models.CharField(max_length=200)
    numero_cnib = models.CharField(max_length=200)
    solde = models.IntegerField(default=0)

    def update_solde(self, amount):
        self.solde += int(amount)
        self.save()

    def __str__(self):
        return "{} {}, cnib: {}, solde: {}".format(self.nom, self.prenoms, self.numero_cnib, self.solde)


class Depot(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    date_depot = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.montant)


class Vente(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('compte', 'Compte'),
        ('orange_money', 'Orange Money'),
        ('liquide', 'Liquide'),
    ]
    montant_vente = models.FloatField(default=0)
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_vente = models.DateTimeField('date vente')
    montant_encaisse = models.IntegerField(default=0)
    monnaie_rendue = models.IntegerField(default=0)
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)
    payment_mode = models.CharField(max_length=12, choices=PAYMENT_MODE_CHOICES, default='liquide')

    def save(self, *args, **kwargs):
        if self.pk is not None:  # If the object already has an ID, then this is an update
            old_vente = Vente.objects.get(pk=self.pk)
            self.revert_transaction(old_vente)

        # Perform the transaction
        if self.payment_mode == 'compte' and self.client is not None:
            self.client.update_solde(-self.montant_vente)
        elif self.payment_mode == 'orange_money':
            CompteOrangeMoney.objects.first().update_montant(self.montant_vente)
        elif self.payment_mode == 'liquide':
            self.vendeur.caisse.update_montant(self.montant_vente)
        super().save(*args, **kwargs)
        # Update transaction history
        if self.client is not None:
            solde_avant = solde_apres = self.client.solde
            if self.payment_mode == 'compte':
                solde_avant += self.montant_vente  # because we already deducted montant_vente
                solde_apres = self.client.solde
            hist_transac = HistoriqueTransactionsClient(client=self.client, montant=self.montant_vente, type_transaction=self.payment_mode, vente=self, solde_avant=solde_avant, solde_apres=solde_apres, date_transaction=timezone.now())
            hist_transac.save()

    def revert_transaction(self, old_vente):
        if old_vente.payment_mode == 'compte' and old_vente.client is not None:
            old_vente.client.update_solde(old_vente.montant_vente)
        elif old_vente.payment_mode == 'orange_money':
            CompteOrangeMoney.objects.first().update_montant(-old_vente.montant_vente)
        elif old_vente.payment_mode == 'liquide':
            old_vente.vendeur.caisse.update_montant(-old_vente.montant_vente)


    def delete(self, *args, **kwargs):
        hist_transac = get_object_or_404(HistoriqueTransactionsClient, vente=self)
        hist_transac.delete()

        # On revert the operation of vente
        if self.payment_mode == 'compte' and self.client is not None:
            self.client.update_solde(self.montant_vente)  # amount back to client
        elif self.payment_mode == 'orange_money':
            CompteOrangeMoney.objects.first().update_montant(-self.montant_vente)  # amount from OM
        elif self.payment_mode == 'liquide':
            self.vendeur.caisse.update_montant(-self.montant_vente)  # amount from cashier

        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class HistoriqueTransactionsClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    type_transaction = models.CharField(max_length=200) #liquide, compte, depot, orange_money
    vente = models.ForeignKey(Vente, blank=True, null=True, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, blank=True, null=True, on_delete=models.CASCADE)
    solde_avant = models.IntegerField(default=0)
    solde_apres = models.IntegerField(default=0)
    date_transaction = models.DateTimeField('date transaction')


    def __str__(self):
        return str(self.montant)

class CompteOrangeMoney(models.Model):
    montant = models.IntegerField(default=0)

    def update_montant(self, amount):
        self.montant += int(amount)
        self.save()

    def __str__(self):
        return str(self.montant)

class HistoriqueDepotRamassageCompteOrangeMoney(models.Model):
    choix_operation = models.TextChoices('choix_operation', 'depot ramassage')
    operateur = models.ForeignKey(User, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    type_operation = models.CharField(choices=choix_operation.choices, max_length=200)
    date_operation = models.DateTimeField('date encaissement')
    
    def __str__(self):
        return "{}, {}, {}, {}".format(self.date_operation, self.type_operation, self.montant, self.operateur)

#fin classes de la caisse


class Categorie(models.Model):
    nom_categorie = models.CharField(max_length=200)

    def __str__(self):
        return self.nom_categorie


class Article(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    nom_article = models.CharField(max_length=200, unique=True)
    code_barres = models.CharField(max_length=200, blank=True, null=True, unique=True) #nouvo
    date_peremption = models.DateTimeField('date peremption', blank=True, null=True) #nouvo
    PAU = models.DecimalField(max_digits=19, decimal_places=2) #prix achat unitaire
    PVU = models.DecimalField(max_digits=19, decimal_places=2) #prix de vente unitaire
    PVG = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True) #prix de vente en gros

    def perime_dans_moins_de(self, jours):
        try:
            return self.date_peremption <= timezone.now() + datetime.timedelta(days=jours)
        except:
            return False
    
    def article_est_perime(self):
        try:
            return self.date_peremption <= timezone.now()
        except:
            return False
    
    @property
    def en_stock(self):
        total_entree = self.entree_set.aggregate(Sum('quantite'))['quantite__sum'] or 0
        total_sortie = self.sortie_set.aggregate(Sum('quantite'))['quantite__sum'] or 0
        total_avarie = self.avarie_set.aggregate(Sum('quantite'))['quantite__sum'] or 0
        return total_entree - total_sortie - total_avarie

    def __str__(self):
        return self.nom_article


class Controle(models.Model):
    controleur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_debut = models.DateTimeField('date debut')
    date_fin = models.DateTimeField('date fin')

    def __str__(self):
        return str(self.date_fin)



class Fournisseur(models.Model):
    reference = models.CharField(max_length=200)
    montant_du_au_fournisseur = models.DecimalField(max_digits=19, decimal_places=2, default=0)

    def __str__(self):
        return str(self.reference)

class Entree(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    date_entree = models.DateTimeField('date operation', default=timezone.now)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, null=True, blank=True)
    paye = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.paye and not self.fournisseur:
            raise ValueError("Fournisseur ne peut pas etre nul quand paye est à false")
        if not self.paye:
            self.fournisseur.montant_du_au_fournisseur += self.article.PAU * Decimal(self.quantite)
            self.fournisseur.save()
        super(Entree, self).save(*args, **kwargs)

    @property
    def reste_a_payer(self):
        if self.paye:
            return 0
        else:
            total_remboursement = RemboursementFournisseur.objects.filter(entree=self).aggregate(Sum('montant'))['montant__sum'] or 0
            return self.article.PAU * self.quantite - total_remboursement

    def __str__(self):
        date_str = self.date_entree.strftime('%d-%m-%Y %H:%M')  # Format de date personnalisé
        return f'{str(self.article)}, qte: {self.quantite}, {self.fournisseur},   {date_str}'


class RemboursementFournisseur(models.Model):
    date = models.DateTimeField('date operation', default=timezone.now)
    entree = models.ForeignKey(Entree, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk is not None:  # si l'objet a déjà un ID, alors il s'agit d'une mise à jour
            old_remboursement = RemboursementFournisseur.objects.get(pk=self.pk)
            # On ajoute d'abord l'ancien montant remboursé au montant dû au fournisseur
            self.fournisseur.montant_du_au_fournisseur += old_remboursement.montant
        if self.fournisseur != self.entree.fournisseur:
            raise ValueError("Fournisseur doit être le même que celui de l'entrée")
        self.fournisseur.montant_du_au_fournisseur -= self.montant  # on soustrait le nouveau montant
        self.fournisseur.save()
        super(RemboursementFournisseur, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.fournisseur.montant_du_au_fournisseur += self.montant
        self.fournisseur.save()
        super(RemboursementFournisseur, self).delete(*args, **kwargs)


class Avarie(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    date_avarie = models.DateTimeField('date operation')

    def __str__(self):
        return str(Article.objects.get(pk=self.article.id))


class Sortie(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    prix_vente_article = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    numero_vente = models.ForeignKey(Vente, on_delete=models.CASCADE)

    def __str__(self):
        return str(Article.objects.get(pk=self.article.id))


class ArretOperation(models.Model):
    date_arret = models.DateTimeField('date arret')

    def __str__(self):
        return str(self.date_arret)

#modif lompo
class ArretCompte(models.Model):
    date_arret = models.DateTimeField(auto_now_add=True)
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE)
    montant_caisse = models.IntegerField(default=0)
