from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


class Fournisseur(models.Model):
    fournisseur = models.CharField(max_length=200)
    tel = models.CharField(max_length=200)
    solde = models.IntegerField(default=0)

    def __str__(self):
        return "{}, solde: {}".format(self.fournisseur, self.solde)


#classes du client
class Client(models.Model):
    nom = models.CharField(max_length=200)
    prenoms = models.CharField(max_length=200)
    numero_cnib = models.CharField(max_length=200)
    solde = models.IntegerField(default=0)

    def __str__(self):
        return "{} {}, cnib: {}, solde: {}".format(self.nom, self.prenoms, self.numero_cnib, self.solde)

class Depot(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    date_depot = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.montant)


class Vente(models.Model):
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_vente = models.DateTimeField('date vente')
    montant_encaisse = models.IntegerField(default=0)
    monnaie_rendue = models.IntegerField(default=0)

    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.CASCADE)

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


#classes de la caisse
class Caisse(models.Model):
    montant = models.IntegerField(default=0)

    def __str__(self):
        return str(self.montant)


class HistoriqueDepotRamassageCaisse(models.Model):
    choix_operation = models.TextChoices('choix_operation', 'depot ramassage')
    operateur = models.ForeignKey(User, on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    type_operation = models.CharField(choices=choix_operation.choices, max_length=200)
    date_operation = models.DateTimeField('date encaissement')
    
    def __str__(self):
        return "{}, {}, {}, {}".format(self.date_operation, self.type_operation, self.montant, self.operateur)
    

class CompteOrangeMoney(models.Model):
    montant = models.IntegerField(default=0)

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
    PAU = models.DecimalField(max_digits=19, decimal_places=2)
    PVU = models.DecimalField(max_digits=19, decimal_places=2)
    PVG = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)

    def perime_dans_moins_de(self, jours):
        try:
            print(self.date_peremption <= timezone.now() + datetime.timedelta(days=jours))
            return self.date_peremption <= timezone.now() + datetime.timedelta(days=jours)
        except:
            return False
    
    def article_est_perime(self):
        try:
            return self.date_peremption <= timezone.now()
        except:
            return False

    def __str__(self):
        return self.nom_article


class Controle(models.Model):
    controleur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_debut = models.DateTimeField('date debut')
    date_fin = models.DateTimeField('date fin')

    def __str__(self):
        return str(self.date_fin)


class Entree(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)
    date_entree = models.DateTimeField('date operation')

    def __str__(self):
        return str(Article.objects.get(pk=self.article.id))


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


