from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from pos.models import ArretCompte, Sortie
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django_datatables_view.base_datatable_view import BaseDatatableView

class SortieListJson(BaseDatatableView):
    model = Sortie
    columns = ['numero_vente__date_vente', 'article', 'quantite']
    order_columns = ['numero_vente__date_vente', 'article', 'quantite']

    def get_initial_queryset(self):
        ac1 = get_object_or_404(ArretCompte, pk=self.kwargs['arret_pk'])
        ac_prev = ArretCompte.objects.filter(vendeur=ac1.vendeur, date_arret__lt=ac1.date_arret).order_by('-date_arret').first()
        if ac_prev is None:
            return Sortie.objects.filter(numero_vente__vendeur=ac1.vendeur).order_by('-pk')
        else:
            return Sortie.objects.filter(numero_vente__vendeur=ac1.vendeur, numero_vente__date_vente__range=[ac_prev.date_arret, ac1.date_arret]).order_by('-pk')

    def render_column(self, row, column):
        if column == 'numero_vente__date_vente':
            # format your date in a way you want
            return row.numero_vente.date_vente.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return super(SortieListJson, self).render_column(row, column)


def liste_sorties_template_view(request, arret_pk):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))

    if request.method == 'GET':
        context = {
            'arret_pk': arret_pk
        }

        return render(request, 'pos/sorties/sorties_list.html', context)


#modif lompo
def liste_sorties_data(request):#100 dernières sorties
    if not request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('pos:login'))
    
    if request.method == 'GET':
        arret_compte = ArretCompte.objects.filter(vendeur=request.user).order_by('-date_arret').first()
        if arret_compte is None:
            sorties = Sortie.objects.filter(numero_vente__vendeur=request.user).order_by('-numero_vente__date_vente')[:100]
        else:
            sorties = Sortie.objects.filter(numero_vente__vendeur=request.user, numero_vente__date_vente__range=[arret_compte.date_arret, timezone.now()])
            
        # Serializing queryset into JSON format
        ma_liste = []
        for sortie in sorties:
            ma_liste.append({
                'article': sortie.article.nom_article,
                'quantite': sortie.quantite,
                'heure': sortie.numero_vente.date_vente.strftime('%d-%m-%Y %H:%M:%S'),
            })
        return JsonResponse(ma_liste, safe=False)
