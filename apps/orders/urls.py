"""
Orders URL configuration.
"""

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('create/', views.order_create, name='create'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/delete/', views.order_delete, name='delete'),
    path('<int:pk>/invoice/', views.order_invoice, name='invoice'),
]
