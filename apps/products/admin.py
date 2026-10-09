"""
Products admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'sku', 'category', 'supplier', 'selling_price', 'quantity', 'is_active')
    list_filter = ('is_active', 'category', 'supplier', 'unit')
    search_fields = ('name', 'sku', 'barcode', 'brand')
    list_editable = ('is_active',)
    readonly_fields = ('barcode', 'created_at', 'updated_at')
    list_per_page = 25

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />', obj.image.url)
        return '—'
    image_preview.short_description = 'Image'
