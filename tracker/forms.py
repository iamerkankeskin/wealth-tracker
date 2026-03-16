from django import forms
from .models import Asset, Transaction


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'asset_type', 'symbol', 'quantity', 'purchase_price', 'current_price', 'currency', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ör. Bitcoin, Apple Hisse, Ev'}),
            'asset_type': forms.Select(attrs={'class': 'form-input', 'id': 'id_asset_type'}),
            'symbol': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ör. BTC, AAPL, GLD'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '0.00'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '0.00'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '0.00 (otomatik çekilir)'}),
            'currency': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Opsiyonel not...'}),
        }
        labels = {
            'name': 'Varlık Adı',
            'asset_type': 'Tip',
            'symbol': 'Sembol',
            'quantity': 'Miktar',
            'purchase_price': 'Alış Fiyatı',
            'current_price': 'Güncel Fiyat',
            'currency': 'Para Birimi',
            'notes': 'Notlar',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symbol'].required = False
        self.fields['notes'].required = False
        self.fields['current_price'].required = False
        self.fields['current_price'].help_text = 'Kripto/hisse/altın için otomatik çekilir. Manuel varlıklar için girin.'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'price_at_time', 'date', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '0.00'}),
            'price_at_time': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '0.00'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Opsiyonel not...'}),
        }
        labels = {
            'transaction_type': 'İşlem Tipi',
            'quantity': 'Miktar',
            'price_at_time': 'İşlem Anındaki Fiyat',
            'date': 'Tarih',
            'notes': 'Notlar',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False
