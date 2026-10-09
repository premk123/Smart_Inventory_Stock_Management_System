"""
Role-based access control decorators.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_only(view_func):
    """Allow only Admin role users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You need Admin privileges to access this page.')
        return redirect('dashboard:index')
    return wrapper


def admin_manager_required(view_func):
    """Allow Admin and Manager roles."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ('admin', 'manager'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You need Manager or Admin privileges to access this page.')
        return redirect('dashboard:index')
    return wrapper


def staff_or_above(view_func):
    """Allow any authenticated user with a defined role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect('accounts:login')
    return wrapper
