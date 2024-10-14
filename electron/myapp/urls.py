from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import admin_dashboard,admin_login,custom_logout
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('oauth/', include('social_django.urls', namespace='social')),

    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('dashboard/category/<str:category>/', views.user_dashboard, name='product_category'),
    
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('products/', views.Product_list, name='product_list'),  # Assuming you have a ProductListView
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-login/', admin_login, name='admin_login'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_authentication/', views.user_authentication, name='user_authentication'),
    path('user_management/', views.user_management, name='user_management'),
    path('category_management/', views.category_management, name='category_management'),
    path('product_management/', views.product_management, name='product_management'),
    path('order_management/', views.order_management, name='order_management'),
    path('inventory_management/', views.inventory_management, name='inventory_management'),
    path('discounts_coupons/', views.discounts_coupons, name='discounts_coupons'), 


    path('product_management/', views.product_list, name='product_management'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),

    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('logout/', custom_logout, name='logout'),

    path('orders/', views.orders, name='orders'),
    path('address/', views.address, name='address'),
    path('switch_account/', views.switch_account, name='switch_account'),

    path('address/', views.address_list, name='address_list'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),

] 
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
               
