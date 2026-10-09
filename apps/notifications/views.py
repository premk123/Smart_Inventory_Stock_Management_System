"""
Notifications views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Notification


@login_required
def notification_list(request):
    """All notifications for the current user."""
    notifs = Notification.objects.filter(
        user=request.user
    ) | Notification.objects.filter(user__isnull=True)
    notifs = notifs.order_by('-created_at')

    # Mark all as read
    notifs.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications/list.html', {
        'notifications': notifs[:50],
        'page_title': 'Notifications',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': '/dashboard/'},
            {'name': 'Notifications', 'url': '#'},
        ],
    })


@login_required
def mark_read(request, pk):
    """Mark a single notification as read via AJAX or redirect."""
    notif = get_object_or_404(Notification, pk=pk)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect(notif.link or 'notifications:list')


@login_required
def mark_all_read(request):
    """Mark all unread notifications as read."""
    Notification.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


@login_required
def unread_count(request):
    """AJAX endpoint returning unread notification count."""
    count = Notification.objects.filter(is_read=False).count()
    return JsonResponse({'count': count})
