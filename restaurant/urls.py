from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    # Customer Menu & Ordering
    path('', views.menu_view, name='menu'),
    path('menu/', views.menu_view, name='menu_redirect'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/sync/', views.sync_cart, name='sync_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Order Tracking
    path('track/', views.track_order_view, name='track_order_search'),
    path('track/<str:order_number>/', views.track_order_view, name='track_order'),
    path('api/order/<str:order_number>/status/', views.order_status_api, name='order_status_api'),

    # Kitchen Display Dashboard
    path('kitchen/', views.kitchen_dashboard_view, name='kitchen_dashboard'),
    path('kitchen/order/<str:order_number>/update/', views.update_order_status, name='update_order_status'),
]
