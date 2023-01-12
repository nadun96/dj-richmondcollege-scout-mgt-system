from django import forms
from .models import Lend
from django.contrib.auth import get_user_model
User = get_user_model()


class LendForm(forms.ModelForm):
    class Meta:
        model = Lend
        fields = ['user', 'item', 'item_quantity_lent']
        widgets = {
            "user": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select the user'}),
            'item': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select the item'}),
            'item_quantity_lent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter the quantity', 'min': '1'})
        }

    # def __init__(self, *args, **kwargs):
    #     super.__init__(*args, **kwargs)
    #     for field in self.fields:


class ReturnLendForm(forms.Form):
    lend = forms.ModelChoiceField(queryset=Lend.objects.filter(
        item_is_lent=True), widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select the record'}))
