"""
Suppliers views — full CRUD.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.core.decorators import admin_manager_required
from .models import Supplier
from .forms import SupplierForm


@login_required
def supplier_list(request):
    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 25))

    qs = Supplier.objects.all()
    if search:
        qs = qs.filter(
            Q(company_name__icontains=search) |
            Q(supplier_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )
    if status:
        qs = qs.filter(is_active=(status == 'active'))

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'suppliers/list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'per_page': per_page,
        'total': qs.count(),
        'page_title': 'Suppliers',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Suppliers', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def supplier_create(request):
    form = SupplierForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully.')
            return redirect('suppliers:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'suppliers/form.html', {
        'form': form,
        'action': 'Add',
        'page_title': 'Add Supplier',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Suppliers', 'url': '/suppliers/'},
            {'name': 'Add', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, request.FILES or None, instance=supplier)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('suppliers:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'suppliers/form.html', {
        'form': form,
        'supplier': supplier,
        'action': 'Update',
        'page_title': f'Edit Supplier – {supplier.company_name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Suppliers', 'url': '/suppliers/'},
            {'name': 'Edit', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def supplier_delete(request, pk):
    if not request.user.can_delete:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('suppliers:list')

    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.company_name
        if supplier.product_set.exists():
            messages.error(request, f'Cannot delete "{name}" — it has associated products.')
        else:
            supplier.delete()
            messages.success(request, f'Supplier "{name}" deleted.')
        return redirect('suppliers:list')

    return render(request, 'suppliers/delete.html', {
        'supplier': supplier,
        'page_title': f'Delete Supplier – {supplier.company_name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Suppliers', 'url': '/suppliers/'},
            {'name': 'Delete', 'url': '#'},
        ],
    })


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    products = supplier.product_set.filter(is_active=True)
    return render(request, 'suppliers/detail.html', {
        'supplier': supplier,
        'products': products,
        'page_title': f'Supplier – {supplier.company_name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Suppliers', 'url': '/suppliers/'},
            {'name': supplier.company_name, 'url': '#'},
        ],
    })
