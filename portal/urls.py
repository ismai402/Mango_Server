from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('cart/', views.cart_view, name='cart'),
    path('products/cart/update/<int:product_id>/',views.update_cart_quantity, name='update_cart_quantity'),
    path('products/add-to-cart/<int:product_id>/',views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('add-product/', views.add_product, name='add_product'),
    path('delete-products/', views.delete_products, name='delete_products'),
    path('orders/', views.order_list, name='order_list'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/', views.product_detail, name='product_detail'),
    # path('products/cart/update/<int:id>/', views.update_cart_quantity, name='update_cart_quantity'),



]
