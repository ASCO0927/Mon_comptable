import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from pos.models import Caisse, ArretCompte
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.views import View
from pos.models import Article
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django import forms
from django.utils import timezone


class ArretCompteForm(forms.ModelForm):
    vendeur = forms.ModelChoiceField(queryset=User.objects.all())

    class Meta:
        model = ArretCompte
        fields = ['vendeur']

#modif lompo
def arret_compte(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    
    if request.method == 'POST':
        if request.method == 'POST':
            vendeur_id = request.POST.get('vendeur') # assuming vendeur is provided as id
            if vendeur_id is not None:
                vendeur = get_object_or_404(User, pk=vendeur_id)
                caisse = get_object_or_404(Caisse, user=vendeur)
                arret_compte = ArretCompte(vendeur=vendeur, montant_caisse=caisse.montant)
                arret_compte.save()
                return HttpResponseRedirect(reverse('pos:arret_compte'))  # assuming 'pos:arret_compte' is the correct url pattern name
            else:
                return HttpResponseBadRequest("Missing 'vendeur' field in request")
    else:
        form = ArretCompteForm()
        arrets_compte = ArretCompte.objects.filter().order_by('-date_arret')
        return render(request, 'pos/arrets_compte/arrets_compte.html', {'arrets_compte': arrets_compte, 'form': form})
