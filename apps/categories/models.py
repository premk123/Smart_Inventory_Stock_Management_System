"""
Category model for product categorization.
"""

from django.db import models


class Category(models.Model):
    """Product category with optional image."""

    name = models.CharField(max_length=100, unique=True, verbose_name='Category Name')
    description = models.TextField(blank=True, default='', verbose_name='Description')
    image = models.ImageField(
        upload_to='categories/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Category Image'
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_product_count(self):
        return self.product_set.filter(is_active=True).count()
