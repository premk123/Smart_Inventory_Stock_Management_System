"""
Reports views — generate inventory, sales, purchase, low stock reports.
Export as CSV, Excel, PDF.
"""

import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone

from apps.products.models import Product
from apps.categories.models import Category
from apps.suppliers.models import Supplier
from apps.orders.models import Order, OrderItem
from apps.stock.models import StockMovement


@login_required
def reports_index(request):
    """Reports dashboard landing page."""
    return render(request, 'reports/index.html', {
        'page_title': 'Reports',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Reports', 'url': '#'},
        ],
    })


@login_required
def inventory_report(request):
    """Full inventory listing with stock value."""
    category_id = request.GET.get('category', '')
    supplier_id = request.GET.get('supplier', '')
    status = request.GET.get('status', 'active')

    qs = Product.objects.select_related('category', 'supplier')
    if category_id:
        qs = qs.filter(category_id=category_id)
    if supplier_id:
        qs = qs.filter(supplier_id=supplier_id)
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    total_value = sum(p.stock_value for p in qs)

    if request.GET.get('export') == 'csv':
        return _export_inventory_csv(qs)
    if request.GET.get('export') == 'excel':
        return _export_inventory_excel(qs)

    return render(request, 'reports/inventory.html', {
        'products': qs,
        'total_value': total_value,
        'categories': Category.objects.filter(is_active=True),
        'suppliers': Supplier.objects.filter(is_active=True),
        'category_id': category_id,
        'supplier_id': supplier_id,
        'status': status,
        'page_title': 'Inventory Report',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Reports', 'url': '/reports/'},
            {'name': 'Inventory', 'url': '#'},
        ],
    })


@login_required
def sales_report(request):
    """Sales report for a date range."""
    date_from = request.GET.get('date_from', (date.today() - timedelta(days=30)).isoformat())
    date_to = request.GET.get('date_to', date.today().isoformat())

    orders = Order.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    ).select_related('created_by')

    total_revenue = orders.filter(status='completed').aggregate(t=Sum('grand_total'))['t'] or 0
    total_orders = orders.count()
    completed = orders.filter(status='completed').count()
    pending = orders.filter(status='pending').count()
    cancelled = orders.filter(status='cancelled').count()

    if request.GET.get('export') == 'csv':
        return _export_sales_csv(orders)

    return render(request, 'reports/sales.html', {
        'orders': orders,
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'completed': completed,
        'pending': pending,
        'cancelled': cancelled,
        'page_title': 'Sales Report',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Reports', 'url': '/reports/'},
            {'name': 'Sales', 'url': '#'},
        ],
    })


@login_required
def low_stock_report(request):
    """Show all products at or below their minimum quantity."""
    products = Product.objects.filter(
        is_active=True, quantity__lte=10
    ).select_related('category', 'supplier').order_by('quantity')

    if request.GET.get('export') == 'csv':
        return _export_low_stock_csv(products)

    return render(request, 'reports/low_stock.html', {
        'products': products,
        'page_title': 'Low Stock Report',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Reports', 'url': '/reports/'},
            {'name': 'Low Stock', 'url': '#'},
        ],
    })


@login_required
def purchase_report(request):
    """Stock-in movements (purchases) for a date range."""
    date_from = request.GET.get('date_from', (date.today() - timedelta(days=30)).isoformat())
    date_to = request.GET.get('date_to', date.today().isoformat())

    movements = StockMovement.objects.filter(
        movement_type='in',
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    ).select_related('product', 'created_by')

    total_units = movements.aggregate(t=Sum('quantity'))['t'] or 0

    return render(request, 'reports/purchase.html', {
        'movements': movements,
        'total_units': total_units,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': 'Purchase Report',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Reports', 'url': '/reports/'},
            {'name': 'Purchase', 'url': '#'},
        ],
    })


# ── CSV Helpers ──────────────────────────────────────────────────────────────

def _export_inventory_csv(qs):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['SKU', 'Product Name', 'Category', 'Supplier', 'Purchase Price', 'Selling Price', 'Stock', 'Unit', 'Stock Value', 'Status'])
    for p in qs:
        writer.writerow([p.sku, p.name, p.category.name, p.supplier.company_name, p.purchase_price, p.selling_price, p.quantity, p.unit, p.stock_value, 'Active' if p.is_active else 'Inactive'])
    return response


def _export_sales_csv(orders):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Customer', 'Phone', 'Date', 'Grand Total', 'Status', 'Payment'])
    for o in orders:
        writer.writerow([o.order_number, o.customer_name, o.customer_phone, o.created_at.strftime('%Y-%m-%d'), o.grand_total, o.status, o.payment_status])
    return response


def _export_low_stock_csv(products):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="low_stock_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['SKU', 'Product', 'Category', 'Current Stock', 'Min Stock', 'Unit'])
    for p in products:
        writer.writerow([p.sku, p.name, p.category.name, p.quantity, p.min_quantity, p.unit])
    return response


def _export_inventory_excel(qs):
    """Export inventory to Excel using openpyxl."""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        return HttpResponse('openpyxl not installed.', status=500)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Inventory Report'

    headers = ['SKU', 'Product Name', 'Category', 'Supplier', 'Purchase Price', 'Selling Price', 'Stock', 'Unit', 'Stock Value', 'Status']
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='1e3a5f', end_color='1e3a5f', fill_type='solid')

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    for row, p in enumerate(qs, 2):
        ws.append([p.sku, p.name, p.category.name, p.supplier.company_name, float(p.purchase_price), float(p.selling_price), p.quantity, p.unit, float(p.stock_value), 'Active' if p.is_active else 'Inactive'])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.xlsx"'
    wb.save(response)
    return response
