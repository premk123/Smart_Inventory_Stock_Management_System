"""
Stock movement forms.
"""

from django import forms
from apps.products.models import Product
from .models import StockMovement


class StockInForm(forms.Form):
    """Form for adding stock."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_stock_product'}),
        label='Product'
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity to add'}),
        label='Quantity'
    )
    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PO / Reference Number'}),
        label='Reference'
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Note'}),
        label='Note'
    )


class StockOutForm(forms.Form):
    """Form for removing stock."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Product'
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity to remove'}),
        label='Quantity'
    )
    movement_type = forms.ChoiceField(
        choices=[
            ('out', 'Stock Out'),
            ('damaged', 'Damaged'),
            ('expired', 'Expired'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Type'
    )
    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference'}),
        label='Reference'
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Note'}),
        label='Note'
    )

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        if product and quantity:
            if quantity > product.quantity:
                raise forms.ValidationError(
                    f'Insufficient stock. Available: {product.quantity} {product.unit}'
                )
        return cleaned_data


class StockAdjustForm(forms.Form):
    """Adjust stock to a specific quantity."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Product'
    )
    new_quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'New stock level'}),
        label='New Quantity'
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for adjustment'}),
        label='Note'
    )
