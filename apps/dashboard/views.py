"""
Dashboard view — aggregates stats from all modules.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta, date
import json

from apps.products.models import Product
from apps.categories.models import Category
from apps.suppliers.models import Supplier
from apps.orders.models import Order, OrderItem
from apps.stock.models import StockMovement
from apps.notifications.models import Notification


@login_required
def dashboard_view(request):
    """Main dashboard with all KPI cards."""
    today = date.today()
    this_month_start = today.replace(day=1)

    # Product stats
    total_products = Product.objects.filter(is_active=True).count()
    low_stock = Product.objects.filter(
        is_active=True, quantity__lte=models_low_quantity()
    ).count()
    out_of_stock = Product.objects.filter(is_active=True, quantity=0).count()

    # Category and supplier
    total_categories = Category.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()

    # Order stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()

    # Revenue
    today_sales = Order.objects.filter(
        created_at__date=today, status='completed'
    ).aggregate(total=Sum('grand_total'))['total'] or 0

    monthly_sales = Order.objects.filter(
        created_at__date__gte=this_month_start, status='completed'
    ).aggregate(total=Sum('grand_total'))['total'] or 0

    total_revenue = Order.objects.filter(
        status='completed'
    ).aggregate(total=Sum('grand_total'))['total'] or 0

    # Profit estimate (revenue - purchase cost of sold items)
    total_profit = 0
    completed_order_items = OrderItem.objects.filter(order__status='completed')
    for item in completed_order_items:
        total_profit += float(item.total_price) - float(item.product.purchase_price * item.quantity)

    # Latest data
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:5]
    latest_orders = Order.objects.order_by('-created_at')[:5]
    recent_stock = StockMovement.objects.order_by('-created_at')[:8]
    latest_notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:5]

    # Low stock products list
    low_stock_products = Product.objects.filter(
        is_active=True, quantity__lte=10
    ).order_by('quantity')[:10]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
        'total_revenue': total_revenue,
        'total_profit': round(total_profit, 2),
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'latest_products': latest_products,
        'latest_orders': latest_orders,
        'recent_stock': recent_stock,
        'latest_notifications': latest_notifications,
        'low_stock_products': low_stock_products,
        'page_title': 'Dashboard',
        'breadcrumb': [{'name': 'Dashboard', 'url': '#'}],
    }
    return render(request, 'dashboard/index.html', context)


def models_low_quantity():
    """Return the low-stock threshold (items at or below their min_quantity)."""
    # This helper is inline because Product.min_quantity varies per product
    # We use a fixed threshold of 10 for count display
    return 10


@login_required
def chart_data_view(request):
    """Return JSON data for all dashboard charts."""
    today = date.today()

    # Monthly sales for last 12 months
    monthly_sales_data = []
    monthly_labels = []
    for i in range(11, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1)

        revenue = Order.objects.filter(
            status='completed',
            created_at__date__gte=month_start,
            created_at__date__lt=month_end
        ).aggregate(t=Sum('grand_total'))['t'] or 0

        monthly_sales_data.append(float(revenue))
        monthly_labels.append(month_start.strftime('%b %Y'))

    # Category distribution
    categories = Category.objects.annotate(
        count=Count('product', filter=Q(product__is_active=True))
    ).filter(count__gt=0).values('name', 'count')

    cat_labels = [c['name'] for c in categories]
    cat_data = [c['count'] for c in categories]

    # Top 5 selling products
    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    top_labels = [p['product__name'] for p in top_products]
    top_data = [p['total_sold'] for p in top_products]

    # Stock analysis (in vs out last 30 days)
    stock_in = StockMovement.objects.filter(
        movement_type='in',
        created_at__date__gte=today - timedelta(days=30)
    ).aggregate(t=Sum('quantity'))['t'] or 0

    stock_out = StockMovement.objects.filter(
        movement_type='out',
        created_at__date__gte=today - timedelta(days=30)
    ).aggregate(t=Sum('quantity'))['t'] or 0

    # Order status breakdown
    order_statuses = Order.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'].capitalize() for s in order_statuses]
    status_data = [s['count'] for s in order_statuses]

    return JsonResponse({
        'monthly_labels': monthly_labels,
        'monthly_sales_data': monthly_sales_data,
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'top_labels': top_labels,
        'top_data': top_data,
        'stock_in': stock_in,
        'stock_out': stock_out,
        'status_labels': status_labels,
        'status_data': status_data,
    })
