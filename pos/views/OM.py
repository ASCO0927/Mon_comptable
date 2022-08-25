from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from ..models import (CompteOrangeMoney, 
                     HistoriqueDepotRamassageCompteOrangeMoney)

def collecte_caisse_orange_money(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        compte_orange_money_list = CompteOrangeMoney.objects.all()
        if len(compte_orange_money_list) == 0:
            compte_orange_money = CompteOrangeMoney(montant=0)
        else:
            compte_orange_money = compte_orange_money_list[0]

        if request.method == 'POST':
            montant_decaissement = request.POST['montant_decaissement']
            now = timezone.now()
            
            compte_orange_money.montant -= int(montant_decaissement)
            compte_orange_money.save()
            
            hist_dep_ram = HistoriqueDepotRamassageCompteOrangeMoney(operateur=User.objects.get(id=user_id), montant=int(montant_decaissement), type_operation="ramassage", date_operation=now)
            hist_dep_ram.save()

            return JsonResponse({'message': 'operation enregistrée avec succes', 'orange_money': compte_orange_money.montant}, status=200)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'orange_money': compte_orange_money.montant}, status=200)
            else:

                liste_dep_ram = []
                for hist in HistoriqueDepotRamassageCompteOrangeMoney.objects.all():
                    jour = hist.date_operation.strftime("%d/%m/%Y")
                    heure = hist.date_operation.strftime("%H:%M")
                    liste_dep_ram.append({'id': hist.id, 'jour': jour, 'heure': heure, 'type_operation': hist.type_operation, 'montant': hist.montant, 'operateur': hist.operateur.username})
                liste_dep_ram.reverse()

                return render(request, 'pos/caisse_orange_money/collecte_caisse_orange_money.html', {'liste_dep_ram': liste_dep_ram})


def depot_caisse_orange_money(request, user_id):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    else:
        compte_orange_money_list = CompteOrangeMoney.objects.all()
        if len(compte_orange_money_list) == 0:
            compte_orange_money = CompteOrangeMoney(montant=0)
        else:
            compte_orange_money = compte_orange_money_list[0]

        if request.method == 'POST':
            montant_encaissement = request.POST['montant_encaissement']
            now = timezone.now()
            
            compte_orange_money.montant += int(montant_encaissement)
            compte_orange_money.save()

            hist_dep_ram = HistoriqueDepotRamassageCompteOrangeMoney(operateur=User.objects.get(id=user_id), montant=int(montant_encaissement), type_operation="depot", date_operation=now)
            hist_dep_ram.save()
            
            return JsonResponse({'message': 'operation enregistrée avec succes', 'orange_money': compte_orange_money.montant}, status=200)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':#request.is_ajax():
                return JsonResponse({'message': 'operation enregistrée avec succes', 'orange_money': compte_orange_money.montant}, status=200)
            else:

                liste_dep_ram = []
                for hist in HistoriqueDepotRamassageCompteOrangeMoney.objects.all():
                    jour = hist.date_operation.strftime("%d/%m/%Y")
                    heure = hist.date_operation.strftime("%H:%M")
                    liste_dep_ram.append({'id': hist.id, 'jour': jour, 'heure': heure, 'type_operation': hist.type_operation, 'montant': hist.montant, 'operateur': hist.operateur.username})
                liste_dep_ram.reverse()

                return render(request, 'pos/caisse_orange_money/depot_caisse_orange_money.html', {'liste_dep_ram': liste_dep_ram})
