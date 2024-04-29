from django import forms
from ..models import RemboursementFournisseur

class RemboursementFournisseurForm(forms.ModelForm):
    class Meta:
        model = RemboursementFournisseur
        fields = ['entree', 'fournisseur', 'montant']
