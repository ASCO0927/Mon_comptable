from django.shortcuts import render, get_object_or_404, redirect
from ..models import Entree, Fournisseur, RemboursementFournisseur
from ..forms.remboursement_fournisseur_forms import RemboursementFournisseurForm

def remboursement_list(request):
    remboursements = RemboursementFournisseur.objects.all()
    return render(request, 'pos/remboursements/remboursement_list.html', {'remboursements': remboursements})


def remboursement_new(request):
    fournisseurs = Fournisseur.objects.filter(montant_du_au_fournisseur__gt=0)
    entrees_all = Entree.objects.all()
    entrees = [entree for entree in entrees_all if entree.reste_a_payer > 0]

    if request.method == "POST":
        form = RemboursementFournisseurForm(request.POST)
        if form.is_valid():
            remboursement = form.save(commit=False)
            remboursement.save()
            return redirect('pos:remboursement_list')
    else:
        form = RemboursementFournisseurForm()
    return render(request, 'pos/remboursements/remboursement_edit.html', {'form': form, 'fournisseurs': fournisseurs, 'entrees': entrees})


def remboursement_detail(request, pk):
    remboursement = get_object_or_404(RemboursementFournisseur, pk=pk)
    return render(request, 'pos/remboursements/remboursement_detail.html', {'remboursement': remboursement})


def remboursement_edit(request, pk):
    remboursement = get_object_or_404(RemboursementFournisseur, pk=pk)
    fournisseurs = Fournisseur.objects.filter(montant_du_au_fournisseur__gt=0)
    entrees_all = Entree.objects.all()
    entrees = [entree for entree in entrees_all if entree.reste_a_payer > 0]

    if request.method == "POST":
        form = RemboursementFournisseurForm(request.POST, instance=remboursement)
        if form.is_valid():
            remboursement = form.save(commit=False)
            remboursement.save()
            return redirect('pos:remboursement_list')
    else:
        form = RemboursementFournisseurForm(instance=remboursement)
    return render(request, 'pos/remboursements/remboursement_edit.html', {'form': form, 'fournisseurs': fournisseurs, 'entrees': entrees})


def remboursement_delete(request, pk):
    remboursement = get_object_or_404(RemboursementFournisseur, pk=pk)
    if request.method=='POST':
        remboursement.delete()
        return redirect('pos:remboursement_list')
    return render(request, 'pos/remboursements/remboursement_confirm_delete.html', {'remboursement': remboursement})
