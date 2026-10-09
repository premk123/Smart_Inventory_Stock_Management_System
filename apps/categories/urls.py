"""
Categories URL configuration.
"""

from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='list'),
    path('create/', views.category_create, name='create'),
    path('<int:pk>/update/', views.category_update, name='update'),
    path('<int:pk>/delete/', views.category_delete, name='delete'),
    path('<int:pk>/', views.category_detail, name='detail'),
]
