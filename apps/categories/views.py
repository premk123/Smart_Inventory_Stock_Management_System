"""
Categories views — full CRUD.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.core.decorators import admin_manager_required
from .models import Category
from .forms import CategoryForm


@login_required
def category_list(request):
    """List all categories with search and pagination."""
    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 25))

    qs = Category.objects.all()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if status:
        qs = qs.filter(is_active=(status == 'active'))

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'categories/list.html', {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'per_page': per_page,
        'total': qs.count(),
        'page_title': 'Categories',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Categories', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def category_create(request):
    """Create a new category."""
    form = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('categories:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'categories/form.html', {
        'form': form,
        'action': 'Create',
        'page_title': 'Create Category',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Categories', 'url': '/categories/'},
            {'name': 'Create', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def category_update(request, pk):
    """Update an existing category."""
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('categories:list')
        messages.error(request, 'Please correct the errors below.')

    return render(request, 'categories/form.html', {
        'form': form,
        'category': category,
        'action': 'Update',
        'page_title': f'Edit Category – {category.name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Categories', 'url': '/categories/'},
            {'name': 'Edit', 'url': '#'},
        ],
    })


@login_required
@admin_manager_required
def category_delete(request, pk):
    """Delete a category (POST only)."""
    if not request.user.can_delete:
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('categories:list')

    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        if category.product_set.exists():
            messages.error(request, f'Cannot delete "{name}" — it has associated products.')
        else:
            category.delete()
            messages.success(request, f'Category "{name}" deleted.')
        return redirect('categories:list')

    return render(request, 'categories/delete.html', {
        'category': category,
        'page_title': f'Delete Category – {category.name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Categories', 'url': '/categories/'},
            {'name': 'Delete', 'url': '#'},
        ],
    })


@login_required
def category_detail(request, pk):
    """View category details and its products."""
    category = get_object_or_404(Category, pk=pk)
    products = category.product_set.filter(is_active=True)
    return render(request, 'categories/detail.html', {
        'category': category,
        'products': products,
        'page_title': f'Category – {category.name}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Categories', 'url': '/categories/'},
            {'name': category.name, 'url': '#'},
        ],
    })
