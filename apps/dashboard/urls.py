"""
Dashboard URL configuration.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('chart-data/', views.chart_data_view, name='chart_data'),
]
