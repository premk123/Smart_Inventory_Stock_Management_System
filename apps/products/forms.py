"""
Product forms.
"""

from django import forms
from .models import Product
from apps.categories.models import Category
from apps.suppliers.models import Supplier


class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""

    class Meta:
        model = Product
        fields = (
            'name', 'sku', 'barcode', 'category', 'supplier', 'brand',
            'purchase_price', 'selling_price', 'quantity',
            'min_quantity', 'max_quantity', 'weight', 'unit',
            'description', 'image', 'is_active'
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU (auto-generated if blank)'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barcode (auto-generated)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10'}),
            'max_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1000'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Product description'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'product_image_input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        self.fields['sku'].required = False
        self.fields['barcode'].required = False

    def clean_selling_price(self):
        purchase = self.cleaned_data.get('purchase_price', 0)
        selling = self.cleaned_data.get('selling_price', 0)
        if selling and purchase and selling < purchase:
            raise forms.ValidationError('Selling price cannot be less than purchase price.')
        return selling

    def clean_sku(self):
        import uuid
        sku = self.cleaned_data.get('sku', '').strip()
        if not sku:
            sku = f'SKU-{uuid.uuid4().hex[:8].upper()}'
        qs = Product.objects.filter(sku=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A product with this SKU already exists.')
        return sku
