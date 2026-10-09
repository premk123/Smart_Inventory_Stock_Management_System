"""
Notification model.
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """System-wide notification for various events."""

    TYPE_LOW_STOCK = 'low_stock'
    TYPE_OUT_OF_STOCK = 'out_of_stock'
    TYPE_NEW_ORDER = 'new_order'
    TYPE_PAYMENT = 'payment'
    TYPE_EXPIRED = 'expired'

    TYPE_CHOICES = [
        (TYPE_LOW_STOCK, 'Low Stock'),
        (TYPE_OUT_OF_STOCK, 'Out of Stock'),
        (TYPE_NEW_ORDER, 'New Order'),
        (TYPE_PAYMENT, 'Payment'),
        (TYPE_EXPIRED, 'Expired'),
    ]

    ICON_MAP = {
        TYPE_LOW_STOCK: 'bi-exclamation-triangle-fill',
        TYPE_OUT_OF_STOCK: 'bi-x-circle-fill',
        TYPE_NEW_ORDER: 'bi-bag-fill',
        TYPE_PAYMENT: 'bi-credit-card-fill',
        TYPE_EXPIRED: 'bi-calendar-x-fill',
    }

    COLOR_MAP = {
        TYPE_LOW_STOCK: 'warning',
        TYPE_OUT_OF_STOCK: 'danger',
        TYPE_NEW_ORDER: 'primary',
        TYPE_PAYMENT: 'success',
        TYPE_EXPIRED: 'secondary',
    }

    title = models.CharField(max_length=200, verbose_name='Title')
    message = models.TextField(verbose_name='Message')
    notification_type = models.CharField(
        max_length=30, choices=TYPE_CHOICES, verbose_name='Type'
    )
    is_read = models.BooleanField(default=False, verbose_name='Read')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    link = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_notification_type_display()}: {self.title}'

    @property
    def icon(self):
        return self.ICON_MAP.get(self.notification_type, 'bi-bell-fill')

    @property
    def color(self):
        return self.COLOR_MAP.get(self.notification_type, 'info')
