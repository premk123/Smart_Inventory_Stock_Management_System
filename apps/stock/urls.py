"""
Stock URL configuration.
"""

from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.stock_list, name='list'),
    path('in/', views.stock_in, name='stock_in'),
    path('out/', views.stock_out, name='stock_out'),
    path('adjust/', views.stock_adjust, name='adjust'),
    path('history/', views.stock_history, name='history'),
    path('summary/', views.stock_summary, name='summary'),
]
