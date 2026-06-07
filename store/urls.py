from django.urls import path
from . import views

urlpatterns = [
    # Home & Products
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('women/', views.women_category, name='women'),
    path('men/', views.men_category, name='men'),
    path('shoes/', views.shoes_category, name='shoes'),
    path('accessories/', views.accessories_category, name='accessories'),
    
    # Cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Analytics Dashboard
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
]
