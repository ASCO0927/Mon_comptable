from django.shortcuts import render, get_object_or_404, redirect
from ..models import Fournisseur
from ..forms.fournisseur_forms import FournisseurForm
from django.contrib.auth.decorators import login_required, user_passes_test

def is_superuser(user):
    return user.is_superuser

@login_required(login_url='pos:login')
@user_passes_test(is_superuser)
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'pos/fournisseurs/fournisseur_list.html', {'fournisseurs': fournisseurs})


@login_required(login_url='pos:login')
@user_passes_test(is_superuser)
def fournisseur_detail(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    return render(request, 'pos/fournisseurs/fournisseur_detail.html', {'fournisseur': fournisseur})


@login_required(login_url='pos:login')
@user_passes_test(is_superuser)
def fournisseur_new(request):
    if request.method == "POST":
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            return redirect('pos:fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'pos/fournisseurs/fournisseur_edit.html', {'form': form})


@login_required(login_url='pos:login')
@user_passes_test(is_superuser)
def fournisseur_edit(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == "POST":
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            fournisseur = form.save()
            return redirect('pos:fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'pos/fournisseurs/fournisseur_edit.html', {'form': form})


@login_required(login_url='pos:login')
@user_passes_test(is_superuser)
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        return redirect('pos:fournisseur_list')
    return render(request, 'pos/fournisseurs/fournisseur_confirm_delete.html', {'fournisseur': fournisseur})
