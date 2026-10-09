"""
Stock movement and adjustment models.
"""

from django.db import models
from django.conf import settings
from apps.products.models import Product


class StockMovement(models.Model):
    """Records every stock in/out event."""

    TYPE_IN = 'in'
    TYPE_OUT = 'out'
    TYPE_ADJUST = 'adjust'
    TYPE_DAMAGED = 'damaged'
    TYPE_EXPIRED = 'expired'

    MOVEMENT_TYPE_CHOICES = [
        (TYPE_IN, 'Stock In'),
        (TYPE_OUT, 'Stock Out'),
        (TYPE_ADJUST, 'Adjustment'),
        (TYPE_DAMAGED, 'Damaged'),
        (TYPE_EXPIRED, 'Expired'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock_movements'
    )
    movement_type = models.CharField(
        max_length=20, choices=MOVEMENT_TYPE_CHOICES, verbose_name='Type'
    )
    quantity = models.IntegerField(verbose_name='Quantity')
    previous_quantity = models.IntegerField(default=0, verbose_name='Previous Stock')
    new_quantity = models.IntegerField(default=0, verbose_name='New Stock')
    reference = models.CharField(
        max_length=200, blank=True, default='', verbose_name='Reference'
    )
    note = models.TextField(blank=True, default='', verbose_name='Note')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} – {self.get_movement_type_display()} ({self.quantity})'
