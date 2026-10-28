
from django import forms
from .models import Portfolio

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['stock_symbol', 'quantity', 'buy_price']
        widgets = {
            'stock_symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Stock Symbol'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'buy_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Buy Price'}),
        }
        