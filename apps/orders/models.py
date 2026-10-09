"""
Order and OrderItem models.
"""

import uuid
from django.db import models
from django.conf import settings
from apps.products.models import Product


class Order(models.Model):
    """Customer sales order."""

    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('cheque', 'Cheque'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
    ]

    order_number = models.CharField(
        max_length=50, unique=True, verbose_name='Order Number'
    )
    invoice_number = models.CharField(
        max_length=50, unique=True, blank=True, verbose_name='Invoice Number'
    )
    customer_name = models.CharField(max_length=200, verbose_name='Customer Name')
    customer_phone = models.CharField(max_length=20, verbose_name='Customer Phone')
    customer_email = models.EmailField(blank=True, default='', verbose_name='Customer Email')
    customer_address = models.TextField(blank=True, default='', verbose_name='Customer Address')
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Discount (₹)'
    )
    gst_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name='GST (%)'
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Tax Amount (₹)'
    )
    shipping_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Shipping Charge (₹)'
    )
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal (₹)'
    )
    grand_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='Grand Total (₹)'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash', verbose_name='Payment Method'
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid', verbose_name='Payment Status'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Order Status'
    )
    note = models.TextField(blank=True, default='', verbose_name='Note')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f'ORD-{uuid.uuid4().hex[:8].upper()}'
        if not self.invoice_number:
            self.invoice_number = f'INV-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    @property
    def status_badge(self):
        badges = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'cancelled': 'danger',
        }
        return badges.get(self.status, 'secondary')

    @property
    def payment_badge(self):
        badges = {
            'paid': 'success',
            'unpaid': 'danger',
            'partial': 'warning',
        }
        return badges.get(self.payment_status, 'secondary')


class OrderItem(models.Model):
    """Individual line item within an order."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items'
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='order_items'
    )
    quantity = models.IntegerField(verbose_name='Quantity')
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Unit Price (₹)'
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='Discount (₹)'
    )
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Total (₹)'
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.total_price = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)
