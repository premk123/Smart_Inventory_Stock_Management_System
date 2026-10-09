"""
Suppliers URL configuration.
"""

from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='list'),
    path('create/', views.supplier_create, name='create'),
    path('<int:pk>/update/', views.supplier_update, name='update'),
    path('<int:pk>/delete/', views.supplier_delete, name='delete'),
    path('<int:pk>/', views.supplier_detail, name='detail'),
]
