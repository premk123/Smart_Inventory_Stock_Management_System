"""
Global context processors — inject notifications and stats into every template.
"""

from apps.notifications.models import Notification


def notifications_processor(request):
    """Inject unread notification count into every template context."""
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(is_read=False).count()
        recent_notifications = Notification.objects.filter(
            is_read=False
        ).order_by('-created_at')[:5]
    else:
        unread_count = 0
        recent_notifications = []

    return {
        'unread_notifications_count': unread_count,
        'recent_notifications': recent_notifications,
    }


def global_stats_processor(request):
    """Inject global navigation stats (low stock count etc.)."""
    context = {}
    if request.user.is_authenticated:
        try:
            from apps.products.models import Product
            context['nav_low_stock_count'] = Product.objects.filter(
                is_active=True, quantity__lte=10, quantity__gt=0
            ).count()
            context['nav_out_of_stock_count'] = Product.objects.filter(
                is_active=True, quantity=0
            ).count()
        except Exception:
            pass
    return context
