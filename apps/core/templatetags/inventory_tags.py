"""
Custom template tags for Smart Inventory.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def currency(value):
    """Format a number as Indian Rupees."""
    try:
        return f'₹{float(value):,.2f}'
    except (TypeError, ValueError):
        return '₹0.00'


@register.filter
def stock_badge(product):
    """Return a Bootstrap badge for stock status."""
    if product.quantity == 0:
        return mark_safe('<span class="badge bg-danger">Out of Stock</span>')
    elif product.quantity <= product.min_quantity:
        return mark_safe('<span class="badge bg-warning text-dark">Low Stock</span>')
    else:
        return mark_safe('<span class="badge bg-success">In Stock</span>')


@register.filter
def multiply(value, arg):
    """Multiply two values."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0


@register.simple_tag
def active_nav(request, url_name):
    """Return 'active' CSS class if current URL matches the given URL name."""
    if request.resolver_match and request.resolver_match.app_name in url_name:
        return 'active'
    return ''


@register.filter
def addclass(field, css_class):
    """Add a CSS class to a form field widget."""
    return field.as_widget(attrs={'class': css_class})


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
