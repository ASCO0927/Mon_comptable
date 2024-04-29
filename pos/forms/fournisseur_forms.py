from django import forms
from ..models import Fournisseur
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ('reference', 'montant_du_au_fournisseur', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save fournisseur'))
