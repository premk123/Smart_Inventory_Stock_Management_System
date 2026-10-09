"""
Products views — full CRUD with filters and search.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from apps.core.decorators import admin_manager_required
from apps.categories.models import Category
from apps.suppliers.models import Supplier
from .models import Product
from .forms import ProductForm


@login_required
def product_list(request):
    search = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    supplier_id = request.GET.get('supplier', '')
    status = request.GET.get('status', '')
    stock_filter = request.GET.get('stock', '')
    per_page = int(request.GET.get('per_page', 25))

    qs = Product.objects.select_related('category', 'supplier')

    if search:
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(barcode__icontains=search) |
            Q(brand__icontains=search)
        )
    if category_id:
        qs = qs.filter(category_id=category_id)
    if supplier_id:
        qs = qs.filter(supplier_id=supplier_id)
    if status:
        qs = qs.filter(is_active=(status == 'active'))
    if stock_filter == 'low':
        qs = qs.filter(quantity__lte=10, quantity__gt=0)
    elif stock_filter == 'out':
        qs = qs.filter(quantity=0)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'products/list.html', {
        'page_obj': page_obj,
        'search': search,
        'category_id': category_id,
        'supplier_id': supplier_id,
        'status': status,
        'stock_filter': stock_filter,
        'per_page': per_page,
        'total': qs.count(),
        'categories': Category.objects.filter(is_active=True),
        'suppliers': Supplier.objects.filter(is_active=True),
        'page_title': 'Products',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Products', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('products:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'products/form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Create Product',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': 'Create', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('products:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'products/form.html', {
        'form': form,
        'product': product,
        'action': 'Update',
        'page_title': f'Edit Product – {product.name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': 'Edit', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def product_delete(request, pk):
    if not request.user.can_delete:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('products:list')

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('products:list')

    return render(request, 'products/delete.html', {
        'product': product,
        'page_title': f'Delete Product – {product.name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': 'Delete', 'url': '#'},
        ],
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    movements = product.stock_movements.order_by('-created_at')[:10]
    return render(request, 'products/detail.html', {
        'product': product,
        'movements': movements,
        'page_title': product.name,
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Products', 'url': '/products/'},
            {'name': product.name, 'url': '#'},
        ],
    })


@login_required
def product_search_api(request):
    """AJAX endpoint for product search in order creation."""
    q = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=q) | Q(sku__icontains=q),
        is_active=True,
        quantity__gt=0
    )[:10]
    data = [{
        'id': p.id,
        'name': p.name,
        'sku': p.sku,
        'selling_price': str(p.selling_price),
        'quantity': p.quantity,
        'unit': p.unit,
    } for p in products]
    return JsonResponse({'products': data})
