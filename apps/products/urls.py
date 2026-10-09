"""
Products URL configuration.
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('create/', views.product_create, name='create'),
    path('<int:pk>/update/', views.product_update, name='update'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('api/search/', views.product_search_api, name='search_api'),
]
