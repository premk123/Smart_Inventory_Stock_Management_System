"""
Custom User model with role-based access control.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user model with roles and profile fields."""

    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_STAFF = 'staff'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_STAFF, 'Staff'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STAFF,
        help_text='User role determines access level.'
    )
    phone = models.CharField(max_length=20, blank=True, default='')
    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    @property
    def is_staff_member(self):
        return self.role == self.ROLE_STAFF

    @property
    def can_delete(self):
        """Only admins and managers can delete."""
        return self.role in [self.ROLE_ADMIN, self.ROLE_MANAGER]

    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default_avatar.png'
