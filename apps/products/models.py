"""
Product model with barcode, SKU, stock tracking.
"""

import uuid
from django.db import models
from apps.categories.models import Category
from apps.suppliers.models import Supplier


class Product(models.Model):
    """Product with full inventory fields."""

    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('ltr', 'Liters'),
        ('mtr', 'Meters'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('dozen', 'Dozen'),
    ]

    name = models.CharField(max_length=200, verbose_name='Product Name')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    barcode = models.CharField(max_length=100, unique=True, blank=True, verbose_name='Barcode')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name='Category'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, verbose_name='Supplier'
    )
    brand = models.CharField(max_length=100, blank=True, default='', verbose_name='Brand')
    purchase_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Purchase Price (₹)'
    )
    selling_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Selling Price (₹)'
    )
    quantity = models.IntegerField(default=0, verbose_name='Current Stock')
    min_quantity = models.IntegerField(default=10, verbose_name='Minimum Quantity')
    max_quantity = models.IntegerField(default=1000, verbose_name='Maximum Quantity')
    weight = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Weight'
    )
    unit = models.CharField(
        max_length=20, choices=UNIT_CHOICES, default='pcs', verbose_name='Unit'
    )
    description = models.TextField(blank=True, default='', verbose_name='Description')
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Product Image'
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} [{self.sku}]'

    def save(self, *args, **kwargs):
        """Auto-generate barcode if not provided."""
        if not self.barcode:
            self.barcode = str(uuid.uuid4()).replace('-', '').upper()[:12]
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity and self.quantity > 0

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    @property
    def profit_margin(self):
        if self.purchase_price and self.purchase_price > 0:
            return round(
                ((self.selling_price - self.purchase_price) / self.purchase_price) * 100, 2
            )
        return 0

    @property
    def stock_value(self):
        return self.quantity * self.purchase_price
