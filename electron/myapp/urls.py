from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import admin_dashboard,admin_login,custom_logout,repair_request_list,add_technician,technician_login
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from .views import delivery_address_list, add_delivery_address, edit_delivery_address, delete_delivery_address
from .views import technician_management,order_management
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_field_name='next'
    ), name='login'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search, name='search'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
   # path('dashboard/', views.user_dashboard, name='dashboard'),
   # path('dashboard/category/<str:category>/', views.user_dashboard, name='product_category'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),
    path('products/', views.Product_list, name='product_list'),  # Assuming you have a ProductListView
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-login/', admin_login, name='admin_login'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_authentication/', views.user_authentication, name='user_authentication'),
    path('user_management/', views.user_management, name='user_management'),
    #path('category_management/', views.category_management, name='category_management'),
    path('product_management/', views.product_management, name='product_management'),
    path('order_management/', views.order_management, name='order_management'),
    path('inventory_management/', views.inventory_management, name='inventory_management'),
    path('discounts_coupons/', views.discounts_coupons, name='discounts_coupons'), 


    path('product_management/', views.product_list, name='product_management'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    

    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('logout/', custom_logout, name='logout'),

    # path('orders/', views.orders, name='orders'),
    path('address/', views.address, name='address'),
    path('orders/', views.orders_view, name='orders'),
    
   

    path('delivery-addresses/', delivery_address_list, name='delivery_address_list'),
    path('delivery-addresses/add/', add_delivery_address, name='add_delivery_address'),
    path('delivery-addresses/edit/<int:address_id>/', edit_delivery_address, name='edit_delivery_address'),
    path('delivery-addresses/delete/<int:address_id>/', delete_delivery_address, name='delete_delivery_address'),
    #path('update_profile/', views.update_profile, name='update_profile'),

    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('user_manage/', views.user_manage, name='user_manage'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),


    path('category/<str:category_name>/', views.product_category, name='product_category'),


    #path('category_management/add/', views.add_category, name='add_category'),
    #path('category_management/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    #path('category_management/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('category-management/', views.category_management, name='category_management'),
    #path('category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),

    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),           
    
    path('checkout/', views.checkout, name='checkout'),
    path('delivery-addresses/', views.delivery_address_list, name='delivery_address_list'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),  # After address selection
    path('payment/', views.payment_response, name='payment'),  # Razorpay payment
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
    path('cart/', views.cart_view, name='cart'),

    #path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase_quantity/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease_quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('save_for_later/<int:product_id>/', views.save_for_later, name='save_for_later'),
    #  path('saved-for-later/', views.view_saved_items, name='view_saved_items'),  
    #path('save_for_later_page/', views.save_for_later_page, name='save_for_later_page'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.your_wishlist, name='your_wishlist'),
    path('cart/', views.view_cart, name='view_cart'),
    # path('remove_saved_items/<int:item_id>/', views.remove_saved_items, name='remove_saved_items'),

    path('delivery-address/', views.delivery_address_list, name='delivery_address_list'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('payment/response/', views.payment_response, name='payment_response'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('logout/', custom_logout, name='logout'),
    #path('response/', views.chatbot_response, name='chatbot_response'),
    #path('wishlist/', views.wishlist_view, name='your_wishlist'),
    path('order/<int:order_id>/pdf/', views.generate_order_pdf, name='order_pdf'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('submit_rating/', views.submit_rating, name='submit_rating'),
    #path('rate-product/', views.rate_product, name='rate_product'),
    path('rate-product/<int:product_id>/', views.rate_product, name='rate_product'),

    path('change-password/', views.change_password, name='change_password'),
    # path('profilee/', views.profilee_view, name='profilee'),
    # path('update_profile/', views.update_profile, name='update_profile'),
    path('profile/', views.profile, name='profile'), 
    path('repair-service/', views.repair_service, name='repair_service'),
    # path('repair-master/login/', views.repair_master_login, name='repair_master_login'),
    # path('repair-master/register/', views.repair_master_register, name='repair_master_register'),
    # path('repair-master/logout/', views.repair_master_logout, name='repair_master_logout'),
    # path('repair-master/dashboard/', views.repair_master_dashboard, name='repair_master_dashboard'),
    path('repair-request/<int:request_id>/<str:status>/', views.update_repair_status, name='update_repair_status'),
    path('repair-master/add-technician/', views.add_technician, name='add_technician'),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_field_name='next'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),
    path('repair-requests/', repair_request_list, name='repair_request_list'),
  
    path('add-technician/', add_technician, name='add_technician'),
    path('technician/login/', technician_login, name='technician_login'),
    # path('save-technician/', save_technician, name='save_technician'),
    path('technician-management/', technician_management, name='technician_management'),

    path('warehouse-locations/', views.warehouse_locations, name='warehouse_locations'),
    path('order-management/', order_management, name='order_management'),
    # path('generate-invoice/', generate_invoice, name='generate_invoice'),
    # ... other URL patterns ...
    path('delivery-data/', views.delivery_data, name='delivery_data'),
    path('predict-delivery-time/<int:order_id>/', views.predict_delivery_time, name='predict_delivery_time'),
    path('repair-requests/edit/<int:pk>/', views.edit_repair_request, name='edit_repair_request'),
    path('repair-requests/delete/<int:pk>/', views.delete_repair_request, name='delete_repair_request'),
]
    




if settings.DEBUG:
      urlpatterns +=  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
               
