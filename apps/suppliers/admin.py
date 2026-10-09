"""
Suppliers admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'supplier_name', 'phone', 'email', 'city', 'is_active', 'created_at')
    list_filter = ('is_active', 'country', 'state')
    search_fields = ('company_name', 'supplier_name', 'phone', 'email')
    list_editable = ('is_active',)

    def image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%;" />', obj.profile_image.url)
        return '—'
    image_preview.short_description = 'Photo'
