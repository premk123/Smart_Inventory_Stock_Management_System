"""
Stock management views — Stock In, Stock Out, Adjust, History, Summary.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum

from apps.products.models import Product
from .models import StockMovement
from .forms import StockInForm, StockOutForm, StockAdjustForm


def _record_movement(product, movement_type, quantity, previous_qty, new_qty, reference, note, user):
    """Helper to save a StockMovement record."""
    StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        previous_quantity=previous_qty,
        new_quantity=new_qty,
        reference=reference,
        note=note,
        created_by=user,
    )


@login_required
def stock_list(request):
    """Current stock overview for all products."""
    search = request.GET.get('q', '')
    stock_filter = request.GET.get('stock', '')
    per_page = int(request.GET.get('per_page', 25))

    qs = Product.objects.filter(is_active=True).select_related('category', 'supplier')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if stock_filter == 'low':
        qs = qs.filter(quantity__lte=10, quantity__gt=0)
    elif stock_filter == 'out':
        qs = qs.filter(quantity=0)
    elif stock_filter == 'normal':
        qs = qs.filter(quantity__gt=10)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'stock/list.html', {
        'page_obj': page_obj,
        'search': search,
        'stock_filter': stock_filter,
        'per_page': per_page,
        'total': qs.count(),
        'low_count': Product.objects.filter(is_active=True, quantity__lte=10, quantity__gt=0).count(),
        'out_count': Product.objects.filter(is_active=True, quantity=0).count(),
        'page_title': 'Stock Overview',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Stock', 'url': '#'},
        ],
    })


@login_required
def stock_in(request):
    """Add stock to a product."""
    form = StockInForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['quantity']
            previous = product.quantity
            product.quantity += qty
            product.save(update_fields=['quantity'])
            _record_movement(
                product, StockMovement.TYPE_IN, qty, previous, product.quantity,
                form.cleaned_data.get('reference', ''),
                form.cleaned_data.get('note', ''),
                request.user
            )
            messages.success(request, f'Added {qty} units to {product.name}. New stock: {product.quantity}')
            return redirect('stock:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'stock/stock_in.html', {
        'form': form,
        'page_title': 'Stock In',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Stock', 'url': '/stock/'},
            {'name': 'Stock In', 'url': '#'},
        ],
    })


@login_required
def stock_out(request):
    """Remove stock from a product."""
    form = StockOutForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['quantity']
            movement_type = form.cleaned_data['movement_type']
            previous = product.quantity
            product.quantity -= qty
            product.save(update_fields=['quantity'])
            _record_movement(
                product, movement_type, qty, previous, product.quantity,
                form.cleaned_data.get('reference', ''),
                form.cleaned_data.get('note', ''),
                request.user
            )
            messages.success(request, f'Removed {qty} units from {product.name}. Remaining: {product.quantity}')
            return redirect('stock:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'stock/stock_out.html', {
        'form': form,
        'page_title': 'Stock Out',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Stock', 'url': '/stock/'},
            {'name': 'Stock Out', 'url': '#'},
        ],
    })


@login_required
def stock_adjust(request):
    """Adjust stock to a specific quantity."""
    form = StockAdjustForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            product = form.cleaned_data['product']
            new_qty = form.cleaned_data['new_quantity']
            previous = product.quantity
            diff = new_qty - previous
            product.quantity = new_qty
            product.save(update_fields=['quantity'])
            _record_movement(
                product, StockMovement.TYPE_ADJUST, abs(diff), previous, new_qty,
                '',
                form.cleaned_data.get('note', ''),
                request.user
            )
            messages.success(request, f'Stock for {product.name} adjusted to {new_qty}.')
            return redirect('stock:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'stock/adjust.html', {
        'form': form,
        'page_title': 'Stock Adjustment',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Stock', 'url': '/stock/'},
            {'name': 'Adjust', 'url': '#'},
        ],
    })


@login_required
def stock_history(request):
    """Full movement history with filters."""
    search = request.GET.get('q', '')
    movement_type = request.GET.get('type', '')
    per_page = int(request.GET.get('per_page', 25))

    qs = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')
    if search:
        qs = qs.filter(Q(product__name__icontains=search) | Q(reference__icontains=search))
    if movement_type:
        qs = qs.filter(movement_type=movement_type)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'stock/history.html', {
        'page_obj': page_obj,
        'search': search,
        'movement_type': movement_type,
        'per_page': per_page,
        'movement_choices': StockMovement.MOVEMENT_TYPE_CHOICES,
        'page_title': 'Stock History',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Stock', 'url': '/stock/'},
            {'name': 'History', 'url': '#'},
        ],
    })


@login_required
def stock_summary(request):
    """Stock summary — total value, totals per category."""
    from apps.categories.models import Category
    from django.db.models import F, ExpressionWrapper, DecimalField

    products = Product.objects.filter(is_active=True).select_related('category')
    total_value = sum(p.stock_value for p in products)
    total_items = products.count()

    # Category-wise summary
    cat_summary = []
    for cat in Category.objects.filter(is_active=True):
        cat_products = products.filter(category=cat)
        cat_summary.append({
            'category': cat,
            'count': cat_products.count(),
            'value': sum(p.stock_value for p in cat_products),
        })

    return render(request, 'stock/summary.html', {
        'products': products[:20],
        'total_value': total_value,
        'total_items': total_items,
        'cat_summary': cat_summary,
        'page_title': 'Stock Summary',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Stock', 'url': '/stock/'},
            {'name': 'Summary', 'url': '#'},
        ],
    })
