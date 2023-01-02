from django import forms
from .models import Lend
from django.contrib.auth import get_user_model
User = get_user_model()


class LendForm(forms.ModelForm):
    class Meta:
        model = Lend
        fields = ['user', 'item', 'item_quantity_lent']

    # def __init__(self, *args, **kwargs):
    #     super.__init__(*args, **kwargs)
    #     for field in self.fields:
