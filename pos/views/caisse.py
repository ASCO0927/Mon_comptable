from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from ..models import (Caisse,
                      HistoriqueDepotRamassageCaisse)


def collecte_caisse(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        caisse_list = Caisse.objects.all()
        if request.method == 'POST':
            montant_decaissement = request.POST['montant_decaissement']
            caisse = get_object_or_404(
                Caisse, id=request.POST.get('caisse_id'))

            now = timezone.now()

            hist_dep_ram = HistoriqueDepotRamassageCaisse(operateur=request.user, caisse=caisse, montant=int(montant_decaissement), type_operation="ramassage", date_operation=now)
            hist_dep_ram.save()

            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
        else:
            liste_dep_ram = []
            for hist in HistoriqueDepotRamassageCaisse.objects.all():
                jour = hist.date_operation.strftime("%d/%m/%Y")
                heure = hist.date_operation.strftime("%H:%M")
                liste_dep_ram.append({'id': hist.id, 'jour': jour, 'heure': heure, 'type_operation': hist.type_operation,
                                     'montant': hist.montant, 'operateur': hist.operateur.username, 'caissier': hist.caisse.user})
            liste_dep_ram.reverse()

            return render(request, 'pos/caisse/collecte_caisse.html', {'liste_dep_ram': liste_dep_ram, 'caisses': caisse_list})


def depot_petite_monnaie(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        caisse_list = Caisse.objects.all()
        if request.method == 'POST':
            montant_decaissement = request.POST['montant_decaissement']
            caisse = get_object_or_404(
                Caisse, id=request.POST.get('caisse_id'))

            now = timezone.now()

            hist_dep_ram = HistoriqueDepotRamassageCaisse(operateur=request.user, caisse=caisse, montant=int(montant_decaissement), type_operation="depot", date_operation=now)
            hist_dep_ram.save()

            return JsonResponse({'message': 'operation enregistrée avec succes', 'caisse': caisse.montant}, status=200)
        else:
            liste_dep_ram = []
            for hist in HistoriqueDepotRamassageCaisse.objects.all():
                jour = hist.date_operation.strftime("%d/%m/%Y")
                heure = hist.date_operation.strftime("%H:%M")
                liste_dep_ram.append({'id': hist.id, 'jour': jour, 'heure': heure, 'type_operation': hist.type_operation,
                                     'montant': hist.montant, 'operateur': hist.operateur.username, 'caissier': hist.caisse.user})
            liste_dep_ram.reverse()

            return render(request, 'pos/caisse/depot_petite_monnaie.html', {'liste_dep_ram': liste_dep_ram, 'caisses': caisse_list})



def ctrl_caisse(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        if request.method == 'GET':
            return render(request, 'pos/ctrl_caisse.html')
