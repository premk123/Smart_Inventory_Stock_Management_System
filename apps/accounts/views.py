"""
Authentication views: login, logout, register, profile, change password, forgot/reset password.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import CustomUser
from .forms import (
    LoginForm, RegisterForm, ProfileUpdateForm,
    CustomPasswordChangeForm, ForgotPasswordForm, SetNewPasswordForm
)


def login_view(request):
    """Handle user login with remember-me support."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def register_view(request):
    """Register a new user (Admin only in production; open here for setup)."""
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.phone = form.cleaned_data.get('phone', '')
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'auth/register.html', {'form': form})


@login_required
def profile_view(request):
    """View user profile."""
    return render(request, 'auth/profile.html', {'user_obj': request.user})


@login_required
def edit_profile_view(request):
    """Edit user profile details."""
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'auth/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Change logged-in user's password."""
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'auth/change_password.html', {'form': form})


def forgot_password_view(request):
    """Send password reset email."""
    form = ForgotPasswordForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            try:
                send_mail(
                    subject='Password Reset – Smart Inventory',
                    message=f'Click the link below to reset your password:\n\n{reset_url}\n\nThis link expires in 24 hours.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                messages.success(request, 'Password reset link sent to your email.')
            except Exception:
                messages.warning(request, 'Could not send email. Please contact the administrator.')
            return redirect('accounts:login')

    return render(request, 'auth/forgot_password.html', {'form': form})


def reset_password_view(request, uidb64, token):
    """Validate token and set new password."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('accounts:forgot_password')

    form = SetNewPasswordForm(user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Password reset successful. Please log in.')
            return redirect('accounts:login')

    return render(request, 'auth/reset_password.html', {'form': form})
