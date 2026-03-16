from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/add/', views.asset_add, name='asset_add'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    path('assets/<int:pk>/transaction/', views.transaction_add, name='transaction_add'),
    path('assets/<int:asset_pk>/transaction/<int:tx_pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('api/refresh/', views.api_refresh_prices, name='api_refresh'),
    path('api/refresh/<int:pk>/', views.api_refresh_single, name='api_refresh_single'),
]
