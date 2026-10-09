"""
Reports URL configuration.
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('inventory/', views.inventory_report, name='inventory'),
    path('sales/', views.sales_report, name='sales'),
    path('low-stock/', views.low_stock_report, name='low_stock'),
    path('purchase/', views.purchase_report, name='purchase'),
]
