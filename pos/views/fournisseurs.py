from django.contrib.auth import logout
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from ..models import Fournisseur
from django.shortcuts import render

"""
def liste_fournisseurs(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            fournisseurs = Fournisseur.objects.all()
            return render(request, 'pos/fournisseur/liste_fournisseurs.html', {'liste_fournisseurs': fournisseurs})


def nouveau_fournisseur(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/fournisseur/nouveau_fournisseur.html')
        else:
            if request.is_ajax():
                client = Client(nom=request.POST['nom_client'].strip(), prenoms=request.POST['prenoms_client'].strip(), numero_cnib=request.POST['numero_cnib_client'])
                client.save()
                
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)

def lst_transactions_client(request, client_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            liste_depots_client = Depot.objects.filter(client = client)
            #liste_transactions_client = HistoriqueTransactionsClient.objects.filter(client = client)

            liste_ventes_au_client = Vente.objects.filter(client = client)

            liste_details_vente = []

            for vente in liste_ventes_au_client:
                liste_articles_vente = []
                montant_vente = 0
                sorties = Sortie.objects.filter(numero_vente=vente.id)
                for sortie in sorties:
                    liste_articles_vente.append({'nom_article': sortie.article.nom_article, 'prix': sortie.article.PVU, 'quantite': sortie.quantite})
                    montant_vente = montant_vente + sortie.article.PVU * sortie.quantite
                hist_trans = HistoriqueTransactionsClient.objects.get(vente = vente)
                solde_avant = hist_trans.solde_avant
                solde_apres = hist_trans.solde_apres
                liste_details_vente.append(
                    {
                        'id': vente.id, 
                        'vendeur': vente.vendeur.username, 
                        'jour': vente.date_vente.strftime("%d/%m/%Y"), 
                        'heure': vente.date_vente.strftime("%H:%M"), 
                        'solde_avant': solde_avant , 
                        'solde_apres': solde_apres, 
                        'articles':liste_articles_vente, 
                        'montant_vente': montant_vente
                    }
                )

            liste_details_depot = []
            for depot in liste_depots_client:
                hist_trans = HistoriqueTransactionsClient.objects.get(depot = depot)
                solde_avant = hist_trans.solde_avant
                solde_apres = hist_trans.solde_apres
                liste_details_depot.append(
                    {
                        'id': depot.id,  
                        'jour': depot.date_depot.strftime("%d/%m/%Y"), 
                        'heure': depot.date_depot.strftime("%H:%M"), 
                        'solde_avant': solde_avant , 
                        'solde_apres': solde_apres, 
                        'montant': depot.montant,
                    }
                )


            return render(request, 'pos/transactions/liste_transactions.html', {'liste_details_depot': liste_details_depot, 'liste_details_vente': liste_details_vente})

def mod_client(request, client_id, *args, **kwargs):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            return render(request, 'pos/client/modifier_client.html', {'client': client})
        else:
            if request.is_ajax():
                client=Client.objects.get(pk = client_id)
                
                client.nom = request.POST['nom_client'].strip()
                client.prenoms = request.POST['prenoms_client'].strip()
                client.numero_cnib = request.POST['numero_cnib_client']
                client.save()
                                
                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def sup_client(request, client_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.is_ajax() and request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            client.delete()
            return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)


def depot_client(request, client_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            client=Client.objects.get(pk = client_id)
            return render(request, 'pos/client/depot_client.html', {"client": client})
        else:
            if request.is_ajax() and request.method == 'POST':
                
                montant_depot = int(request.POST['montant'])

                depot = Depot(client=Client.objects.get(pk = request.POST['client_id']), montant=montant_depot, date_depot=timezone.now())
                depot.save()

                #maj solde
                client=Client.objects.get(pk = client_id)
                solde_avant = int(client.solde)
                solde_apres = solde_avant + montant_depot
                client.solde = solde_apres
                client.save()

                #hist transact
                hist_transac = HistoriqueTransactionsClient(client=client, montant = montant_depot, type_transaction="depot", depot=depot, solde_avant=solde_avant, solde_apres=solde_apres, date_transaction=datetime.now())
                hist_transac.save()

                caisse_list = Caisse.objects.all()
                if len(caisse_list) == 0:
                    caisse = Caisse(montant=0)
                else:
                    caisse = caisse_list[0]
                caisse.montant += montant_depot
                caisse.save()

                return JsonResponse({'message': 'operation enregistrée avec succes'}, status=200)
"""