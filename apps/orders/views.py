"""
Orders views — create, list, detail, status update, invoice.
"""

import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse

from apps.core.decorators import admin_manager_required
from apps.products.models import Product
from apps.stock.models import StockMovement
from .models import Order, OrderItem
from .forms import OrderForm, OrderStatusForm


@login_required
def order_list(request):
    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    payment = request.GET.get('payment', '')
    per_page = int(request.GET.get('per_page', 25))

    qs = Order.objects.select_related('created_by').prefetch_related('items')
    if search:
        qs = qs.filter(
            Q(order_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    if status:
        qs = qs.filter(status=status)
    if payment:
        qs = qs.filter(payment_status=payment)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'orders/list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'payment': payment,
        'per_page': per_page,
        'total': qs.count(),
        'page_title': 'Orders',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Orders', 'url': '#'},
        ],
    })


@login_required
def order_create(request):
    """Create order with dynamic product rows via JavaScript."""
    form = OrderForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Parse product rows from hidden JSON field
            items_json = request.POST.get('items_data', '[]')
            try:
                items = json.loads(items_json)
            except (json.JSONDecodeError, ValueError):
                items = []

            if not items:
                messages.error(request, 'Please add at least one product to the order.')
                return render(request, 'orders/create.html', {
                    'form': form,
                    'page_title': 'Create Order',
                })

            order = form.save(commit=False)
            order.created_by = request.user

            # Calculate totals
            subtotal = Decimal('0')
            for item in items:
                qty = int(item.get('quantity', 1))
                price = Decimal(str(item.get('unit_price', 0)))
                item_discount = Decimal(str(item.get('discount', 0)))
                subtotal += (price * qty) - item_discount

            gst_amount = subtotal * (order.gst_percent / 100)
            order.subtotal = subtotal
            order.tax_amount = gst_amount
            order.grand_total = subtotal + gst_amount + order.shipping_charge - order.discount
            order.save()

            # Save order items and reduce stock
            for item in items:
                product = get_object_or_404(Product, pk=item['product_id'])
                qty = int(item.get('quantity', 1))
                price = Decimal(str(item.get('unit_price', 0)))
                item_discount = Decimal(str(item.get('discount', 0)))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=price,
                    discount=item_discount,
                )
                # Reduce stock
                prev_qty = product.quantity
                product.quantity = max(0, product.quantity - qty)
                product.save(update_fields=['quantity'])
                StockMovement.objects.create(
                    product=product,
                    movement_type='out',
                    quantity=qty,
                    previous_quantity=prev_qty,
                    new_quantity=product.quantity,
                    reference=order.order_number,
                    note=f'Order {order.order_number}',
                    created_by=request.user,
                )

            # Create notification for new order
            from apps.notifications.models import Notification
            Notification.objects.create(
                title='New Order Created',
                message=f'Order #{order.order_number} for {order.customer_name} — ₹{order.grand_total}',
                notification_type='new_order',
                link=f'/orders/{order.pk}/',
            )

            messages.success(request, f'Order #{order.order_number} created successfully.')
            return redirect('orders:detail', pk=order.pk)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'orders/create.html', {
        'form': form,
        'page_title': 'Create Order',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Orders', 'url': '/orders/'},
            {'name': 'Create', 'url': '#'},
        ],
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product')

    status_form = OrderStatusForm(request.POST or None, instance=order)
    if request.method == 'POST':
        if status_form.is_valid():
            status_form.save()
            messages.success(request, 'Order status updated.')
            return redirect('orders:detail', pk=pk)

    return render(request, 'orders/detail.html', {
        'order': order,
        'items': items,
        'status_form': status_form,
        'page_title': f'Order #{order.order_number}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Orders', 'url': '/orders/'},
            {'name': order.order_number, 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def order_delete(request, pk):
    if not request.user.can_delete:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('orders:list')

    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Order #{order_number} deleted.')
        return redirect('orders:list')

    return render(request, 'orders/delete.html', {
        'order': order,
        'page_title': f'Delete Order #{order.order_number}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Orders', 'url': '/orders/'},
            {'name': 'Delete', 'url': '#'},
        ],
    })


@login_required
def order_invoice(request, pk):
    """Render printable invoice."""
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product')
    return render(request, 'orders/invoice.html', {
        'order': order,
        'items': items,
    })
