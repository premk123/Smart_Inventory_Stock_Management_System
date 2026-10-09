"""
Supplier model.
"""

from django.db import models


class Supplier(models.Model):
    """Supplier / Vendor model."""

    company_name = models.CharField(max_length=200, verbose_name='Company Name')
    supplier_name = models.CharField(max_length=200, verbose_name='Contact Person')
    phone = models.CharField(max_length=20, verbose_name='Phone')
    email = models.EmailField(verbose_name='Email')
    gst_number = models.CharField(max_length=50, blank=True, default='', verbose_name='GST Number')
    address = models.TextField(verbose_name='Address')
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State')
    country = models.CharField(max_length=100, default='India', verbose_name='Country')
    pincode = models.CharField(max_length=20, verbose_name='Pincode')
    profile_image = models.ImageField(
        upload_to='suppliers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Profile Image'
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['company_name']

    def __str__(self):
        return f'{self.company_name} – {self.supplier_name}'

    def get_product_count(self):
        return self.product_set.filter(is_active=True).count()
