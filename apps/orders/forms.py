"""
Order forms.
"""

from django import forms
from .models import Order, OrderItem
from apps.products.models import Product


class OrderForm(forms.ModelForm):
    """Order header form."""

    class Meta:
        model = Order
        fields = (
            'customer_name', 'customer_phone', 'customer_email',
            'customer_address', 'discount', 'gst_percent',
            'shipping_charge', 'payment_method', 'payment_status',
            'status', 'note'
        )
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optional)'}),
            'customer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'gst_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.01'}),
            'shipping_charge': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Order note'}),
        }


class OrderStatusForm(forms.ModelForm):
    """Quick status update form."""

    class Meta:
        model = Order
        fields = ('status', 'payment_status')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
        }
