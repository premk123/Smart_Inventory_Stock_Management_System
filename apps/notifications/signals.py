"""
Django signals for auto-generating notifications on stock events and order creation.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='products.Product')
def check_low_stock(sender, instance, **kwargs):
    """Create low-stock or out-of-stock notification when stock is updated."""
    from apps.notifications.models import Notification

    if instance.is_out_of_stock:
        # Avoid duplicate notifications
        if not Notification.objects.filter(
            notification_type='out_of_stock',
            title__contains=instance.name,
            is_read=False
        ).exists():
            Notification.objects.create(
                title=f'Out of Stock: {instance.name}',
                message=f'Product "{instance.name}" (SKU: {instance.sku}) is now out of stock.',
                notification_type=Notification.TYPE_OUT_OF_STOCK,
                link=f'/products/{instance.pk}/',
            )
    elif instance.is_low_stock:
        if not Notification.objects.filter(
            notification_type='low_stock',
            title__contains=instance.name,
            is_read=False
        ).exists():
            Notification.objects.create(
                title=f'Low Stock Alert: {instance.name}',
                message=f'Product "{instance.name}" has only {instance.quantity} {instance.unit} remaining.',
                notification_type=Notification.TYPE_LOW_STOCK,
                link=f'/products/{instance.pk}/',
            )
