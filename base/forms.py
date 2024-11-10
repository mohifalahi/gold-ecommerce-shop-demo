from django import forms

from .models import Wallet


class WalletDepositForm(forms.ModelForm):
    deposit = forms.IntegerField(label="deposit")

    class Meta:
        model = Wallet
        fields = []
        widgets = {
            'deposit': forms.TextInput(attrs={'class': 'form-control'})
        }