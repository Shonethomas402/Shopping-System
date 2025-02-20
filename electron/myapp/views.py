from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
from django.db.models import Prefetch
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal
import json
import logging
import pandas as pd
import os
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.db.models import Q

from django.http import JsonResponse
from django.shortcuts import render
from .models import Order
from django.shortcuts import get_object_or_404, redirect
from .models import Cart, Product

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Order, Cart, CartItems, OrderItem
import razorpay

def home(request):
    products = Product.objects.all()
    #categories = Category.objects.all()  # Fetching categories
    context = {
        'products': products,
        #'categories': categories,  # Adding categories to context
    }
    return render(request, 'homepage.html', context)

# Add placeholder views for register, login, cart, profile, and search
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Hash the password
            user.save()
            profile = Profile(user=user)
            profile.location = form.cleaned_data.get('location')
            profile.phone_no = form.cleaned_data.get('phone_number')
            print(form.cleaned_data.get('phone_number'))
            profile.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            print(f"User is_superuser: {user.is_superuser}")  # Debug print
            
            # Explicitly check if user is superuser
            if user.is_superuser:
                print("Redirecting to admin dashboard")  # Debug print
                return redirect('admin_dashboard')
            else:
                print("Redirecting to user dashboard")  # Debug print
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout(request):
    logout()
    request.session.clear()
    return redirect('login')

def cart(request):
     cart, created = Cart.objects.get_or_create(user=request.user)
    # Show only items that are not marked as saved for later
     products_in_cart = cart.items.filter(saved_for_later=False)
     context = {'products_in_cart': products_in_cart}
     return render(request, 'cart.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, Product


def save_for_later(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the item is already saved to avoid duplicates
    saved_item, created = SavedForLaterItem.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, 'Product saved for later.')
    else:
        messages.info(request, 'This product is already in your saved items.')
    
    # Redirect to the cart or any other relevant page
    return redirect('view_saved_items') 

# views.py
# from .models import SavedForLaterItem
# @login_required
# def view_saved_items(request):
#     saved_items = SavedForLaterItem.objects.filter(user=request.user).select_related('product')
#     return render(request, 'saved_for_later.html', {'saved_items': saved_items})
# def remove_saved_items(request, item_id):
#     item = get_object_or_404(SavedForLaterItem, pk=item_id)
#     if request.method == "POST":
#         item.delete()
#     return redirect('view_saved_items')
@login_required
def profile(request):
    # Get recent orders with delivery status
    recent_orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]  # Get last 5 orders

    # Get counts for dashboard
    orders_count = Order.objects.filter(user=request.user).count()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    context = {
        'user': request.user,
        'recent_orders': recent_orders,
        'orders_count': orders_count,
        'wishlist_count': wishlist_count,
    }
    
    return render(request, 'profile.html', context)

def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    # Base queryset
    products = Product.objects.all()

    # Apply search query
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # Apply category filter
    if category:
        products = products.filter(category_id=category)

    # Apply price range filter
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Apply sorting
    if sort:
        if sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')
        elif sort == 'name_asc':
            products = products.order_by('name')
        elif sort == 'name_desc':
            products = products.order_by('-name')

    # Get categories for filter
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }

    return render(request, 'search.html', context)

from django.shortcuts import render, redirect
from .models import Product, Category  # Ensure you import necessary models
from .forms import UserLoginForm  # Assuming you have a form for login

def user_dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    # If the user is authenticated, display products on the dashboard
    if request.user.is_authenticated:
        # Fetch all products
        products = Product.objects.all()
        categories = Category.objects.all()
        
        return render(request, 'user_dashboard.html', {'products': products, 'categories': categories})

    

# In views.py
from django.shortcuts import render




def Product_list(request):
    return render(request,'product_list.html')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User

# Check if the user is a superuser (admin)
def admin_required(user):
    return user.is_superuser
 #Ensure only admin users can access this view
@login_required
@user_passes_test(admin_required)  # Add this decorator
def admin_dashboard(request):
    """
    View for the admin dashboard
    """
    if not request.user.is_superuser:
        return redirect('user_dashboard')
    
    context = {
        'user': request.user,
        # Add any other context data needed for the admin dashboard
    }
    return render(request, 'admin_dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from .forms import UserLoginForm  # Ensure you have the form defined or imported

def admin_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser:
                auth_login(request, user)
                return redirect('admin_dashboard')  # Redirect to admin dashboard
    else:
        form = UserLoginForm()

    return render(request, 'admin_login.html', {'form': form})


from django.shortcuts import render

# def admin_dashboard(request):
#     return render(request, 'admin_dashboard.html')

def user_authentication(request):
    return render(request, 'user_authentication.html')

def user_management(request):
    users = User.objects.all()  
    return render(request, 'user_authentication.html', {'users': users})

# views.py
from django.shortcuts import render, redirect
from .models import Category
from django.http import HttpResponse


def category_management(request):
    if request.method == 'POST':
        # Handle form submission
        category_name = request.POST.get('name')
        if category_name:
            # Create a new category and save to the database
            Category.objects.create(name=category_name)
            return redirect('category_management')  # Redirect to the category management page after saving

    # Fetch existing categories to display in the table
    categories = Category.objects.all()
    
    return render(request, 'category_management.html', {'categories': categories})


# Delete Category
# views.py
from django.shortcuts import get_object_or_404, redirect
from .models import Category

def delete_category(request, pk):
    # Get the category object to be deleted
    category = get_object_or_404(Category, pk=pk)

    # Delete the category
    category.delete()

    # Redirect back to the category management page
    return redirect('category_management')




def product_management(request):
   products = Product.objects.all()
   return render(request, 'product_management.html' , {'products': products}) 

from django.shortcuts import render
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def order_management(request):
    # Get all orders and separate them by status
    completed_orders = Order.objects.filter(status='Completed').order_by('-created_at')
    pending_orders = Order.objects.filter(status='Pending').order_by('-created_at')
    
    context = {
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'order_management.html', context)
@login_required
def generate_orders_report_pdf(request):
    try:
        completed_orders = Order.objects.filter(status='Completed').order_by('-created_at')
        pending_orders = Order.objects.filter(status='Pending').order_by('-created_at')
        
        template = get_template('order_pdf_template.html')
        context = {
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'total_completed': completed_orders.count(),
            'total_pending': pending_orders.count(),
            'now': timezone.now(),
        }
        
        html = template.render(context)
        result = BytesIO()
        
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"orders_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        return HttpResponse('Error generating PDF', status=400)
    
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('order_management')

def inventory_management(request):
    return render(request, 'inventory_management.html')

def discounts_coupons(request):
    
    return render(request, 'discounts_coupons.html')


from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm

# View to display products
def product_list(request):
    products = Product.objects.all()
    # In your views.py product_list function
    

    return render(request, 'product_list.html', {'products': products})

# View to add a new product
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# View to edit an existing product
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_edit.html', {'form': form})

# View to delete a product
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_management')
    return render(request, 'product_confirm_delete.html', {'product': product})



  # Redirect to the cart view or any other page
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get or create an active cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    
    # Get or create a cart item for the product
    cart_item, created = CartItems.objects.get_or_create(cart=cart, product=product)
    
    # Check stock before adding
    if cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"{product.name} added to cart successfully!")
    else:
        messages.warning(request, f"Sorry, {product.name} is out of stock!")
    
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    
    if not cart:
        messages.info(request, "Your cart is empty")
        return render(request, 'cart.html', {'products_in_cart': [], 'total_price': 0})

    cart_items = CartItems.objects.filter(cart=cart)
    total_price = sum(item.product_total() for item in cart_items)

    context = {
        'products_in_cart': cart_items,
        'total_price': total_price,
    }

    return render(request, 'cart.html', context)


def remove_from_cart(request, product_id):
    try:
        # Fetch the active cart for the user
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart:
            messages.error(request, "No active cart found.")
            return redirect('view_cart')

        # Get the cart item to remove
        cart_item = get_object_or_404(CartItems, cart=cart, product_id=product_id)

        # Delete the cart item
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    except CartItems.DoesNotExist:
        messages.error(request, "Item not found in cart.")

    return redirect('view_cart')
def checkout(request):

    if request.method == 'POST':
        # Redirect to delivery address selection page
        return redirect('delivery_address_list')
    cart_items = CartItems.objects.filter(cart__user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})



from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('login')


def increase_quantity(request, product_id):
    try:
        # Get the user's active cart
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart:
            messages.error(request, "No active cart found.")
            return redirect('view_cart')

        # Get the cart item to increase quantity
        cart_item = get_object_or_404(CartItems, cart=cart, product_id=product_id)

        # Check stock before increasing
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Quantity increased.")
        else:
            messages.warning(request, "Not enough stock available.")

    except CartItems.DoesNotExist:
        messages.error(request, "Item not found in cart.")

    return redirect('view_cart')
def decrease_quantity(request, product_id):
    try:
        # Get the user's active cart
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart:
            messages.error(request, "No active cart found.")
            return redirect('view_cart')

        # Get the cart item to decrease quantity
        cart_item = get_object_or_404(CartItems, cart=cart, product_id=product_id)

        # Decrease the quantity
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, "Quantity decreased.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")

    except CartItems.DoesNotExist:
        messages.error(request, "Item not found in cart.")

    return redirect('view_cart')


from django.shortcuts import render


@login_required
def orders(request):
    print("Orders view accessed")  # Debugging line
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)

def address(request):
    # Logic for fetching and displaying user orders can go here
    return render(request, 'address.html')
def switch_account(request):
   return render(request, 'switch_account.html')

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
  
    return render(request, 'product_detail.html', {'product': product})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import DeliveryAddress
from .forms import DeliveryAddressForm  # Ensure you have a form for DeliveryAddress

@login_required
def delivery_address_list(request):
    addresses = DeliveryAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if not selected_address_id:
            messages.error(request, "Please select a delivery address")
            return redirect('delivery_address_list')
            
        # Store the selected address ID in session
        request.session['selected_address'] = selected_address_id
        return redirect('confirm_order')  # Redirect to confirm order page
        
    return render(request, 'delivery_address_list.html', {'addresses': addresses})


def add_delivery_address(request):
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST)
        if form.is_valid():
            delivery_address = form.save(commit=False)
            delivery_address.user = request.user  # Associate the address with the logged-in user
            delivery_address.save()
            return redirect('delivery_address_list')  # Redirect to the list of addresses
    else:
        form = DeliveryAddressForm()
    return render(request, 'add_delivery_address.html', {'form': form})

def edit_delivery_address(request, address_id):
    
    delivery_address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    if request.method == 'POST':
        form = DeliveryAddressForm(request.POST, instance=delivery_address)
        if form.is_valid():
            form.save()
            return redirect('delivery_address_list')
    else:
        form = DeliveryAddressForm(instance=delivery_address)
    return render(request, 'edit_delivery_address.html', {'form': form, 'address': delivery_address})

def delete_delivery_address(request, address_id):
    delivery_address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)
    delivery_address.delete()
    return redirect('delivery_address_list')

def buy_now(request, product_id):
    # Logic for the "Buy Now" action, such as adding the product to the cart and redirecting to checkout
    # For now, let's redirect the user to the checkout page
    return redirect('checkout')


# @login_required
# def update_profile(request):
#     try:
#         profilee = request.user.profilee
#     except Profilee.DoesNotExist:
#         profilee = Profilee.objects.create(user=request.user)

#     if request.method == 'POST':
#         form = ProfileeUpdateForm(request.POST, instance=profilee)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully!')
#             return redirect('profilee')
#     else:
#         form = ProfileeUpdateForm(instance=profilee)
#     return render(request, 'update_profile.html', {'form': form})

# @login_required
# def profilee_view(request):
#     try:
#         profilee = request.user.profilee
#     except Profilee.DoesNotExist:
#         profilee = Profilee.objects.create(user=request.user)
#     return render(request, 'profilee.html', {'profilee': profilee})
@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})
@login_required
def user_manage(request):
    users = User.objects.all()
    return render(request, 'user_manage.html', {'users': users})



def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
  
    user .blocked = True  # Set the blocked field to True
    user.save()
    return redirect('user_manage')

@login_required
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
  
    user.blocked = False  # Set the blocked field to False
    user.save()
    return redirect('user_manage')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Category


def category_management(request):
    if request.method == 'POST':
        category_name = request.POST.get('name', '').strip()

        # Validation for characters only
        # if not re.match(r'^[A-Za-z\s]+$', category_name):
        #     messages.error(request, 'Category name must contain only letters and spaces.')
        #     return redirect('category_management')

        # Check for duplicate category
        if Category.objects.filter(name__iexact=category_name).exists():
            messages.error(request, 'Category name already exists.')
            return redirect('category_management')

        # Create new category if all validations pass
        new_category = Category(name=category_name)
        new_category.save()
        messages.success(request, 'Category added successfully!')
        return redirect('category_management')

    # Fetch all categories to display in the table
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    return render(request, 'category_management.html', context)

# Delete category function (optional)
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('category_management')


from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_category(request, category_name):
    # Fetch the category by its name
    category = get_object_or_404(Category, name=category_name)
    # Get all products related to this category
    products = Product.objects.filter(category=category)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'product_category.html', context)



def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failure(request):
    return render(request, 'payment_failure.html')


import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart,DeliveryAddress, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def cart_view(request):
    # Fetch items for the cart and items saved for later
    products_in_cart = CartItems.objects.filter(cart__user=request.user, saved_for_later=False)
    products_saved_for_later = CartItems.objects.filter(cart__user=request.user, saved_for_later=True)

    # Calculate total price for items in the cart
    total_price = sum(item.product.price * item.quantity for item in products_in_cart)

    # Pass necessary data to the cart template
    context = {
        'products_in_cart': products_in_cart,
        'products_saved_for_later': products_saved_for_later,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def payment_response(request):
    try:
        if request.method == "POST":
            payment_data = json.loads(request.body)
            razorpay_payment_id = payment_data.get('razorpay_payment_id')
            razorpay_order_id = payment_data.get('razorpay_order_id')
            razorpay_signature = payment_data.get('razorpay_signature')

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)

            # Get the order and update it
            order = Order.objects.get(payment_id=razorpay_order_id)
            order.status = 'Completed'
            order.payment_id = razorpay_payment_id 
            order.save()

            # Clear the cart only after successful payment
            cart = Cart.objects.filter(user=request.user, is_active=True).first()
            if cart:
                # Update product stock
                cart_items = CartItems.objects.filter(cart=cart)
                for item in cart_items:
                    product = item.product
                    product.stock -= item.quantity
                    product.save()
        

                # Deactivate the cart instead of deleting it
                cart.is_active = False
                cart.save()

            # Clear session data
            request.session.pop('selected_address', None)
            request.session.pop('current_order_id', None)

            return JsonResponse({
                'status': 'success',
                'message': 'Payment processed successfully',
                'order_id': order.id
            })

    except Exception as e:
        logger.error(f"Error in payment_response: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)



import logging

# Configure logger
logger = logging.getLogger(__name__)
def confirm_order(request):
    try:
        # Check if address is selected
        selected_address_id = request.session.get('selected_address')
        if not selected_address_id:
            messages.error(request, "Please select a delivery address")
            return redirect('delivery_address_list')

        # Get active cart items
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
        if not cart:
            messages.error(request, "Your cart is empty")
            return redirect('view_cart')

        cart_items = CartItems.objects.filter(cart=cart)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty")
            return redirect('view_cart')

        # Calculate total price
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        total_price_paise = int(float(total_price) * 100)  # Convert to paise for Razorpay

        # Create Razorpay Order
        try:
            payment_order = client.order.create({
                'amount': total_price_paise,
                'currency': "INR",
                'payment_capture': '1'
            })
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            messages.error(request, "Payment gateway error. Please try again.")
            return redirect('view_cart')

        # Create Order in database
        order = Order.objects.create(
            user=request.user,
            status='Pending',
            total_price=total_price,
            payment_id=payment_order['id'],
            address_id=selected_address_id
        )
        logger.debug(f"Order created: {order.id} with payment_id: {order.payment_id}")

        # Create OrderItems
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
            request.session['current_order_id'] = order.id


        # Prepare context for payment
        context = {
            'order': order,
            'cart_items': cart_items,
            'total_price': total_price,
            'razorpay_order_id': payment_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_API_KEY,
            'razorpay_amount': total_price_paise,
            'callback_url': request.build_absolute_uri(reverse('payment_response')),
        }

        return render(request, 'payment.html', context)

    except Exception as e:
        logger.error(f"Error in confirm_order: {str(e)}")
        messages.error(request, "An error occurred while processing your order")
        return redirect('view_cart')




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Wishlist
from django.http import JsonResponse



# @login_required
# def add_to_wishlist(request, product_id):
#     if request.method == 'POST':
#         try:
#             product = get_object_or_404(Product, pk=product_id)
            
#             # Delete any duplicate wishlists
#             Wishlist.objects.filter(user=request.user).delete()
            
#             # Create a new wishlist or get the existing one
#             wishlist, created = Wishlist.objects.get_or_create(user=request.user)
#             wishlist.products.add(product)
            
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Product added to wishlist'
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'message': str(e)
#             })
    
#     return JsonResponse({
#         'success': False,
#         'message': 'Invalid request method'
#     })

# @login_required
# def remove_from_wishlist(request, product_id):
#     if request.method == 'POST':
#         try:
#             product = get_object_or_404(Product, pk=product_id)
#             wishlist = Wishlist.objects.filter(user=request.user).first()
            
#             if wishlist:
#                 wishlist.products.remove(product)
                
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Product removed from wishlist'
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'message': str(e)
#             })
    
#     return JsonResponse({
#         'success': False,
#         'message': 'Invalid request method'
#     })

# @login_required
# def view_wishlist(request):
#     try:
#         wishlist = Wishlist.objects.get(user=request.user)
#         wishlist_products = wishlist.products.all()
#     except Wishlist.DoesNotExist:
#         wishlist_products = []
    
#     context = {
#         'wishlist_products': wishlist_products
#     }
#     return render(request, 'wishlist.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Wishlist

@login_required
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Added to wishlist'
                })
            
            messages.success(request, 'Product added to wishlist!')
            return redirect('your_wishlist')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            messages.error(request, 'Error adding to wishlist')
            return redirect('user_dashboard')

@login_required
def remove_from_wishlist(request, product_id):
    if request.method == 'POST':
        try:
            wishlist_item = get_object_or_404(Wishlist, 
                user=request.user, 
                product_id=product_id
            )
            wishlist_item.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Removed from wishlist'
                })
            
            messages.success(request, 'Product removed from wishlist!')
            return redirect('your_wishlist')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            messages.error(request, 'Error removing from wishlist')
            return redirect('your_wishlist')

@login_required
def your_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'wishlist.html', context)
import logging

logger = logging.getLogger(__name__)

def create_order(user, total_price, payment_order, selected_address_id):
    try:
        order = Order.objects.create(
            user=user,
            status='Pending',
            total_price=total_price,
            payment_id=payment_order['id'],
            address_id=selected_address_id
        )
        logger.info(f"Order created: {order.id}")
        return order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise
import csv
import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order



# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Order
# from delivery_prediction.src.model import DeliveryPredictor
# import os
# import csv

# @login_required
# def orders_view(request):
#     orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
#     # Initialize the predictor
#     predictor = DeliveryPredictor()
    
#     # Path to the training data file
#     training_data_file = os.path.join(settings.BASE_DIR, 'Brazillian_e-commerce_Final.csv')  # Update the path accordingly

#     # Read training data from the CSV file
#     training_data = []
#     try:
#         with open(training_data_file, mode='r') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 training_data.append({
#                     'order_id': int(row['order_id']),
#                     'feature1': float(row['feature1']),
#                     'feature2': float(row['feature2']),
#                     'delivery_time': float(row['delivery_time']),
#                 })
#     except FileNotFoundError:
#         # Handle the case where the file does not exist
#         return render(request, 'orders.html', {'orders': orders, 'error': 'Training data file not found.'})
#     except Exception as e:
#         # Handle any other exceptions
#         return render(request, 'orders.html', {'orders': orders, 'error': str(e)})

#     # Train the model with the loaded training data
#     predictor.train(training_data)

#     # Prepare data for predictions
#     order_ids = [order.id for order in orders]
#     features = predictor.prepare_features(order_ids)
    
#     # Get predictions
#     predictions = predictor.predict(features)
    
#     # Create a mapping of order IDs to predictions
#     order_predictions = {order.id: prediction for order, prediction in zip(orders, predictions)}
#     print(order_predictions)
    
#     return render(request, 'orders.html', {'orders': orders, 'order_predictions': order_predictions})

def wishlist_view(request):
    # Replace with logic to fetch the user's wishlist items if needed
    wishlist_items = []  # Example placeholder for wishlist data
    
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import io
from django.shortcuts import get_object_or_404
from .models import Order

def generate_order_pdf(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add company logo/header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "Electronics Shop")
    
    # Add order information
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 700, f"Order #{order.id}")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 670, f"Date: {order.created_at.strftime('%d %B %Y')}")
    p.drawString(50, 650, f"Customer: {order.user.get_full_name() or order.user.username}")
    p.drawString(50, 630, f"Status: {order.status}")
    
    # Create table for order items
    data = [['Product', 'Quantity', 'Price', 'Total']]
    for item in order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f"₹{item.product.price}",
            f"₹{item.product_total}"
        ])
    
    # Add total row
    data.append(['', '', 'Total:', f"₹{order.total_price}"])
    
    # Create the table
    table = Table(data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    # Draw the table
    table.wrapOn(p, 50, 50)
    table.drawOn(p, 50, 500)
    
    # Add footer
    p.setFont("Helvetica", 10)
    p.drawString(50, 50, "Thank you for shopping with us!")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'order_{order.id}.pdf')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product,Rating

@login_required
def product_detail(request, id):  # Add 'id' parameter here
    product = get_object_or_404(Product, id=id)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(user=request.user, product=product).first()
    
    context = {
        'product': product,
        'user_rating': user_rating
    }
    return render(request, 'product_detail.html', context)
@login_required
def rate_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating_value = request.POST.get('rating')
        
        if rating_value:
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'rating': rating_value}
            )
            
            if not created:
                rating.rating = rating_value
                rating.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
        return redirect('product_detail', id=product_id)
    return redirect('product_detail', id=product_id)

@login_required
def submit_rating(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        score = request.POST.get('score')

        product = get_object_or_404(Product, id=product_id)
        rating, created = Rating.objects.update_or_create(
            user=request.user, product=product,
            defaults={'score': score}
        )
        return JsonResponse({'success': True, 'message': 'Rating submitted successfully!'})

    return JsonResponse({'success': False, 'message': 'Invalid request!'})

# new user
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import RepairRequest
def repair_service(request):
    # Get completed repair requests
    completed_requests = RepairRequest.objects.filter(status='completed').order_by('-created_at')
    
    if request.method == 'POST':
        try:
            # Get form data
            device_type = request.POST.get('device_type')
            proof_of_purchase = request.FILES.get('proof_of_purchase')
            issue_description = request.POST.get('issue_description')
            pin_number = request.POST.get('pin_number')

            # Validate required fields
            if not all([device_type, proof_of_purchase, issue_description, pin_number]):
                messages.error(request, 'All fields are required')
                return render(request, 'repair_service.html', {'completed_requests': completed_requests})

            # Create repair request
            repair_request = RepairRequest.objects.create(
                device_type=device_type,
                proof_of_purchase=proof_of_purchase,
                issue_description=issue_description,
                pin_number=pin_number
            )

            messages.success(request, f'Repair request submitted successfully! Your PIN number is: {pin_number}')
            return redirect('repair_service')

        except Exception as e:
            messages.error(request, f'Error submitting repair request: {str(e)}')
            return render(request, 'repair_service.html', {'completed_requests': completed_requests})

    return render(request, 'repair_service.html', {'completed_requests': completed_requests})

# def repair_service(request):
#     if request.method == 'POST':
#         if 'delete_request' in request.POST:
#             request_id = request.POST.get('request_id')
#             try:
#                 repair_request = RepairRequest.objects.get(id=request_id)
#                 repair_request.delete()
#                 messages.success(request, 'Repair request deleted successfully.')
#             except RepairRequest.DoesNotExist:
#                 messages.error(request, 'Repair request not found.')
#             return redirect('repair_service')
    
#     completed_requests = RepairRequest.objects.filter(status='completed').order_by('-created_at')
#     context = {
#         'completed_requests': completed_requests,
#     }
#     return render(request, 'repair_service.html', context)

def update_repair_status(request, request_id, status):
    """Handle repair request status updates"""
    if request.method == 'POST':
        try:
            repair_request = get_object_or_404(RepairRequest, id=request_id)
            
            # Update status
            if status in ['pending', 'approved', 'rejected']:
                repair_request.status = status
                repair_request.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Status updated to {status}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid status'
                })
                
        except RepairRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Repair request not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.http import JsonResponse
# from .models import RepairRequest,Technician
# from django.contrib.auth.hashers import make_password, check_password

# def repair_master_register(request):
#     if request.method == 'POST':
#         try:
#             # Get form data
#             name = request.POST.get('name')
#             email = request.POST.get('email')
#             phone = request.POST.get('phone')
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirm_password')

#             # Validate required fields
#             if not all([name, email, phone, password, confirm_password]):
#                 messages.error(request, 'All fields are required')
#                 return redirect('repair_master_register')

#             # Check if passwords match
#             if password != confirm_password:
#                 messages.error(request, 'Passwords do not match')
#                 return redirect('repair_master_register')

#             # Check if email already exists
#             if RepairMaster.objects.filter(email=email).exists():
#                 messages.error(request, 'Email already registered')
#                 return redirect('repair_master_register')

#             # Create repair master
#             repair_master = RepairMaster.objects.create(
#                 name=name,
#                 email=email,
#                 phone=phone,
#                 password=make_password(password)  # Hash the password
#             )

#             messages.success(request, 'Registration successful! Please login.')
#             return redirect('repair_master_login')

#         except Exception as e:
#             messages.error(request, f'Error during registration: {str(e)}')
#             return redirect('repair_master_register')

#     return render(request, 'repair_master_register.html')

# def repair_master_login(request):
#     if request.method == 'POST':
#         try:
#             email = request.POST.get('email')
#             password = request.POST.get('password')

#             # Validate required fields
#             if not all([email, password]):
#                 messages.error(request, 'All fields are required')
#                 return redirect('repair_master_login')

#             # Check if repair master exists
#             try:
#                 repair_master = RepairMaster.objects.get(email=email)
#             except RepairMaster.DoesNotExist:
#                 messages.error(request, 'Invalid email or password')
#                 return redirect('repair_master_login')

#             # Verify password
#             if check_password(password, repair_master.password):
#                 # Store repair master id in session
#                 request.session['repair_master_id'] = repair_master.id
#                 messages.success(request, 'Login successful!')
#                 return redirect('repair_master_dashboard')
#             else:
#                 messages.error(request, 'Invalid email or password')
#                 return redirect('repair_master_login')

#         except Exception as e:
#             messages.error(request, f'Error during login: {str(e)}')
#             return redirect('repair_master_login')

#     return render(request, 'repair_master_login.html')

# def repair_master_logout(request):
#     # Clear repair master session
#     if 'repair_master_id' in request.session:
#         del request.session['repair_master_id']
#     messages.success(request, 'Logged out successfully')
#     return redirect('repair_master_login')

# def repair_master_dashboard(request):
#     # Check if repair master is logged in
#     repair_master_id = request.session.get('repair_master_id')
#     if not repair_master_id:
#         messages.error(request, 'Please login first')
#         return redirect('repair_master_login')
    
#     try:
#         # Get repair master and their technicians
#         repair_master = RepairMaster.objects.get(id=repair_master_id)
#         repair_requests = RepairRequest.objects.all().order_by('-created_at')
#         technicians = Technician.objects.filter(repair_master=repair_master).order_by('-created_at')
        
#         context = {
#             'repair_master': repair_master,
#             'repair_requests': repair_requests,
#             'technicians': technicians,  # Add technicians to context
#             'title': 'Repair Master Dashboard'
#         }
#         return render(request, 'repair_master_dashboard.html', context)
    
#     except RepairMaster.DoesNotExist:
#         messages.error(request, 'Invalid session')
#         return redirect('repair_master_login')
#     except Exception as e:
#         messages.error(request, f'Error: {str(e)}')
#         return redirect('repair_master_login')

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from .models import  Technician

# def add_technician(request):
#     repair_master_id = request.session.get('repair_master_id')
#     if not repair_master_id:
#         messages.error(request, 'Please login first')
#         return redirect('repair_master_login')
    
#     try:
#         repair_master = RepairMaster.objects.get(id=repair_master_id)
        
#         if request.method == 'POST':
#             name = request.POST.get('name')
#             pin_no = request.POST.get('pin_no')
            
#             # Validate required fields
#             if not all([name, pin_no]):
#                 messages.error(request, 'All fields are required')
#                 return redirect('add_technician')
            
#             # Check if PIN is unique
#             if Technician.objects.filter(pin_no=pin_no).exists():
#                 messages.error(request, 'This PIN number is already in use')
#                 return redirect('add_technician')
            
#             # Create new technician
#             technician = Technician.objects.create(
#                 name=name,
#                 pin_no=pin_no,
#                 repair_master=repair_master
#             )
            
#             messages.success(request, 'Technician added successfully!')
#             return redirect('repair_master_dashboard')
        
#         return render(request, 'add_technician.html', {'repair_master': repair_master})
    
#     except RepairMaster.DoesNotExist:
#         messages.error(request, 'Invalid session')
#         return redirect('repair_master_login')
#     except Exception as e:
#         messages.error(request, f'Error: {str(e)}')
#         return redirect('repair_master_dashboard')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import RepairRequest

def repair_request_list(request):
    if request.method == 'POST':
        if 'delete_request' in request.POST:
            request_id = request.POST.get('request_id')
            try:
                repair_request = RepairRequest.objects.get(id=request_id)
                repair_request.delete()
                messages.success(request, 'Repair request deleted successfully.')
            except RepairRequest.DoesNotExist:
                messages.error(request, 'Repair request not found.')
            return redirect('repair_request_list')
    
    repair_requests = RepairRequest.objects.all().order_by('-created_at')
    return render(request, 'repair_requests_list.html', {'repair_requests': repair_requests})

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
  # Assuming you have a Technician model

def add_technician(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pin_number = request.POST.get('pin_no')
        email = request.POST.get('email')

        # Create a new Technician instance
        technician = Technician(name=name, pin_number=pin_number, email=email)
        try:
            technician.save()
            messages.success(request, f'Technician {name} added successfully!')
            return redirect('technician_management')  # Redirect to technician management page
        except Exception as e:
            messages.error(request, f'Error adding technician: {str(e)}')
            return redirect('add_technician')  # Redirect back to add form if there's an error

    return render(request, 'add_technician.html')


# def tech_login(request):
#     if request.method == 'POST':
#         name = request.POST.get('name').strip()
#         email = request.POST.get('email').strip().lower()
#         pin = request.POST.get('pin').strip()
#         role = request.POST.get('role')

#         try:
#             # Print form data for debugging
#             print(f"Form data - Name: '{name}', Email: '{email}', PIN: '{pin}'")
            
#             # First try to find any similar email addresses to help with typos
#             similar_techs = Technician.objects.filter(email__icontains=email.split('@')[0])
            
#             if similar_techs.exists():
#                 # If we found similar emails, check if any match exactly
#                 tech = similar_techs.filter(email__iexact=email).first()
#                 if tech:
#                     if tech.name.lower() == name.lower() and tech.pin_number == pin:
#                         # Successful login
#                         request.session['technician_id'] = tech.id
#                         request.session['technician_name'] = tech.name
#                         request.session['technician_role'] = role
#                         messages.success(request, 'Login successful!')
#                         return redirect('tech_dashboard')
#                     else:
#                         if tech.name.lower() != name.lower():
#                             messages.error(request, 'Name does not match our records.')
#                         else:
#                             messages.error(request, 'Invalid PIN number.')
#                 else:
#                     # Found similar emails but none match exactly
#                     suggestions = [t.email for t in similar_techs]
#                     messages.error(request, f'Did you mean one of these emails? {", ".join(suggestions)}')
#             else:
#                 messages.error(request, 'No technician found with this email address.')
            
#             # Print all technicians for debugging
#             print("\nAll technicians in database:")
#             for tech in Technician.objects.all():
#                 print(f"DB Tech - Name: '{tech.name}', Email: '{tech.email}', PIN: '{tech.pin_number}'")
            
#         except Exception as e:
#             print(f"Login error: {str(e)}")
#             messages.error(request, f'An error occurred: {str(e)}')

#     return render(request, 'tech_login.html')



# @login_required
# def tech_dashboard(request):
#     if request.method == 'POST':
#         request_id = request.POST.get('request_id')
#         action = request.POST.get('action')
        
#         try:
#             repair_request = get_object_or_404(RepairRequest, id=request_id)
            
#             if action == 'accept':
#                 repair_request.status = 'approved'
#                 messages.success(request, 'Repair request accepted successfully.')
            
#             elif action == 'reject':
#                 repair_request.status = 'rejected'
#                 messages.warning(request, 'Repair request rejected.')
            
#             elif action == 'complete':
#                 repair_request.status = 'completed'
#                 messages.success(request, 'Repair request marked as completed.')
            
#             repair_request.save()
#             return redirect('tech_dashboard')
            
#         except Exception as e:
#             messages.error(request, f'Error processing request: {str(e)}')
    
#     # Get lists of requests for display
#     pending_requests = RepairRequest.objects.filter(status='pending').order_by('-created_at')
#     active_requests = RepairRequest.objects.filter(status='approved').order_by('-created_at')
    
#     context = {
#         'pending_requests': pending_requests,
#         'active_requests': active_requests,
#         'technician': request.user,  # Add logged-in technician info
#     }
    
#     return render(request, 'techdashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Technician, DeliveryBoy, RepairRequest

def tech_login(request):
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip().lower()
        pin = request.POST.get('pin').strip()
        role = request.POST.get('role')

        # Handle Delivery Boy Login
        if role == 'deliveryboy':
            try:
                deliveryboy = DeliveryBoy.objects.get(email=email)
                if deliveryboy.name.lower() == name.lower() and deliveryboy.pin_number == pin:
                    request.session['deliveryboy_id'] = deliveryboy.id
                    request.session['deliveryboy_name'] = deliveryboy.name
                    request.session['role'] = 'deliveryboy'
                    messages.success(request, 'Login successful!')
                    return redirect('deliveryboy_dashboard')
                else:
                    if deliveryboy.name.lower() != name.lower():
                        messages.error(request, 'Name does not match our records.')
                    else:
                        messages.error(request, 'Invalid PIN number.')
            except DeliveryBoy.DoesNotExist:
                messages.error(request, 'No delivery boy found with this email address.')

        # Handle Technician Login
        elif role == 'technician':
            try:
                similar_techs = Technician.objects.filter(email__icontains=email.split('@')[0])
                
                if similar_techs.exists():
                    tech = similar_techs.filter(email__iexact=email).first()
                    if tech:
                        if tech.name.lower() == name.lower() and tech.pin_number == pin:
                            request.session['technician_id'] = tech.id
                            request.session['technician_name'] = tech.name
                            request.session['technician_role'] = role
                            messages.success(request, 'Login successful!')
                            return redirect('tech_dashboard')
                        else:
                            if tech.name.lower() != name.lower():
                                messages.error(request, 'Name does not match our records.')
                            else:
                                messages.error(request, 'Invalid PIN number.')
                    else:
                        suggestions = [t.email for t in similar_techs]
                        messages.error(request, f'Did you mean one of these emails? {", ".join(suggestions)}')
                else:
                    messages.error(request, 'No technician found with this email address.')
            
            except Exception as e:
                print(f"Login error: {str(e)}")
                messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'tech_login.html')

@login_required
def tech_dashboard(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        try:
            repair_request = get_object_or_404(RepairRequest, id=request_id)
            
            if action == 'accept':
                repair_request.status = 'approved'
                messages.success(request, 'Repair request accepted successfully.')
            elif action == 'reject':
                repair_request.status = 'rejected'
                messages.warning(request, 'Repair request rejected.')
            elif action == 'complete':
                repair_request.status = 'completed'
                messages.success(request, 'Repair request marked as completed.')
            
            repair_request.save()
            return redirect('tech_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error processing request: {str(e)}')
    
    pending_requests = RepairRequest.objects.filter(status='pending').order_by('-created_at')
    active_requests = RepairRequest.objects.filter(status='approved').order_by('-created_at')
    
    context = {
        'pending_requests': pending_requests,
        'active_requests': active_requests,
        'technician': request.user,
    }
    
    return render(request, 'techdashboard.html', context)

def deliveryboy_dashboard(request):
    if 'deliveryboy_id' not in request.session:
        messages.error(request, 'Please login first!')
        return redirect('tech_login')
    
    deliveryboy_id = request.session.get('deliveryboy_id')
    deliveryboy_name = request.session.get('deliveryboy_name')
    
    # Get today's date
    today = timezone.now().date()
    
    # Get pending deliveries (in_transit)
    pending_deliveries = Order.objects.filter(
        delivery_boy_id=deliveryboy_id,
        delivery_status='in_transit',
        created_at__date=today
    ).order_by('created_at')

    # Get accepted deliveries
    accepted_deliveries = Order.objects.filter(
        delivery_boy_id=deliveryboy_id,
        delivery_status='accepted',
        created_at__date=today
    ).order_by('created_at')

    # Get completed deliveries
    completed_deliveries = Order.objects.filter(
        delivery_boy_id=deliveryboy_id,
        delivery_status='delivered',
        created_at__date=today
    ).order_by('created_at')

    # Check if this delivery boy has less than 3 orders for today
    total_orders = pending_deliveries.count() + accepted_deliveries.count() + completed_deliveries.count()
    
    if total_orders < 3:
        # Calculate how many more orders can be assigned
        available_slots = 3 - total_orders
        
        # Get unassigned orders
        new_orders = Order.objects.filter(
            status='Completed',
            delivery_status__isnull=True,
            created_at__date=today
        ).order_by('created_at')[:available_slots]
        
        # Assign these orders to the delivery boy
        for order in new_orders:
            order.delivery_boy_id = deliveryboy_id
            order.delivery_status = 'in_transit'
            order.save()
        
        # Refresh pending deliveries
        pending_deliveries = Order.objects.filter(
            delivery_boy_id=deliveryboy_id,
            delivery_status='in_transit',
            created_at__date=today
        ).order_by('created_at')

    context = {
        'deliveryboy_name': deliveryboy_name,
        'pending_deliveries': pending_deliveries,
        'accepted_deliveries': accepted_deliveries,
        'completed_deliveries': completed_deliveries,
        'orders_count': total_orders,
        'max_orders': 3,
    }
    return render(request, 'deliveryboy_dashboard.html', context)

@login_required
def accept_delivery(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        # Generate OTP when delivery is accepted
        if not order.delivery_otp:
            import random
            order.delivery_otp = str(random.randint(100000, 999999))
        order.delivery_status = 'accepted'
        order.save()
        messages.success(request, 'Delivery accepted successfully!')
        return redirect('deliveryboy_dashboard')

@login_required
def verify_delivery_otp(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        entered_otp = request.POST.get('otp')
        
        if entered_otp == order.delivery_otp:
            from django.utils import timezone
            order.otp_verified = True
            order.delivery_time = timezone.now()  # Record delivery time
            order.delivery_status = 'delivered'
            order.save()
            messages.success(request, 'Delivery completed successfully!')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            
    return redirect('deliveryboy_dashboard')

def logout_user(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('tech_login')

def technician_management(request):
    if request.method == 'POST':
        if 'delete_technician' in request.POST:
            technician_id = request.POST.get('technician_id')
            try:
                technician = Technician.objects.get(id=technician_id)
                technician.delete()
                messages.success(request, f'Technician {technician.name} deleted successfully.')
            except Technician.DoesNotExist:
                messages.error(request, 'Technician not found.')
            return redirect('technician_management')
    
    technicians = Technician.objects.all().order_by('name')
    return render(request, 'technician_management.html', {'technicians': technicians})

 # Ensure you have this template# Ensure you have this template 

def technician_login(request):
       if request.method == 'POST':
           # Logic to handle login
           username = request.POST.get('username')
           password = request.POST.get('password')
           # Add your authentication logic here
           if username and password:  # Replace with actual validation
               # Assuming successful login, redirect to the dashboard
               messages.success(request, 'Login successful!')
               return redirect('tech_dashboard')  # Change to your actual dashboard URL name
           else:
               messages.error(request, 'Invalid credentials. Please try again.')
               return render(request, 'technician_login.html')

from django.shortcuts import render
from .models import Warehouse 




def warehouse_locations(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact')  # Note: form field name is 'contact'
        capacity = request.POST.get('capacity')
        description = request.POST.get('description')

        try:
            # Create new warehouse
            warehouse = Warehouse.objects.create(
                name=name,
                address=address,
                contact_number=contact_number,
                capacity=capacity,
                description=description
            )
            messages.success(request, 'Warehouse added successfully!')
            return redirect('warehouse_locations')
        except Exception as e:
            messages.error(request, f'Error adding warehouse: {str(e)}')
            
    # GET request - display warehouses
    warehouses = Warehouse.objects.all().order_by('-created_at')
    return render(request, 'warehouse_locations.html', {'warehouses': warehouses})

from django.shortcuts import render
import pandas as pd
import os
import numpy as np

def delivery_data(request):
    # Load the dataset
    csv_path = os.path.join(os.path.dirname(__file__), 'datasets', 'delivery_time_dataset.csv')
    df = pd.read_csv(csv_path)

    # Convert DataFrame to a list of dictionaries for easy rendering in the template
    delivery_data = df.to_dict(orient='records')

    return render(request, 'delivery_data.html', {'delivery_data': delivery_data})

def predict_delivery_time(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Construct the path to the delivery time dataset
    dataset_path = os.path.join(os.path.dirname(__file__), 'datasets', 'delivery_time_dataset.csv')
    
    try:
        # Load the delivery time dataset
        df = pd.read_csv(dataset_path)
        
        # Get the delivery location from the order
        delivery_place = order.address.place.strip()
        delivery_place = ''.join([i for i in delivery_place if not i.isdigit()]).strip()
        delivery_place = delivery_place.replace('(', '').replace(')', '').strip()
        
        # Get current time as order placement time
        order_placement_time = order.created_at
        
        # Find similar deliveries in the dataset based on location
        similar_deliveries = df[df['delivery_location'].str.contains(delivery_place, case=False, na=False)]
        
        if not similar_deliveries.empty:
            # Calculate average delivery time for the location
            avg_delivery_days = similar_deliveries['delivery_time'].mean()
            
            # Round to nearest whole number of days
            delivery_days = round(avg_delivery_days)
            
            # Convert order placement time to datetime if it's not already
            if isinstance(order_placement_time, str):
                order_placement_time = datetime.strptime(order_placement_time, '%Y-%m-%d %H:%M:%S.%f')
            
            # Calculate predicted delivery datetime
            predicted_datetime = order_placement_time + timedelta(days=delivery_days)
            
            # Ensure delivery time is between 9 AM and 5 PM
            delivery_hour = random.randint(9, 16)  # 16 to allow for minutes
            delivery_minute = random.choice([0, 15, 30, 45])
            predicted_datetime = predicted_datetime.replace(hour=delivery_hour, minute=delivery_minute, second=0, microsecond=0)
            
            delivery_info = f"Expected delivery by {predicted_datetime.strftime('%d %b %Y %I:%M %p')}"
            
            # Log the prediction details
            logger.info(f"Order {order_id} - Location: {delivery_place}")
            logger.info(f"Average delivery days for location: {avg_delivery_days}")
            logger.info(f"Predicted delivery time: {predicted_datetime}")
            
        else:
            delivery_info = "Delivery estimate: 3-5 business days, delivery between 9:00 AM - 5:00 PM"
            
    except Exception as e:
        logger.error(f"Error predicting delivery time: {str(e)}")
        delivery_info = "Delivery estimate: 3-5 business days, delivery between 9:00 AM - 5:00 PM"

    return render(request, 'predict_delivery_time.html', {
        'order': order,
        'predicted_time': delivery_info,
        'order_time': order.created_at.strftime('%d %b %Y %I:%M %p')
    })

@login_required
def order_pdf(request, order_id):
    """Generate PDF for a specific order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Draw things on the PDF
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, f"Order Invoice #{order.id}")
    
    # Customer Info
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Customer: {order.user.get_full_name() or order.user.username}")
    p.drawString(50, 700, f"Date: {order.created_at.strftime('%d %B %Y')}")
    p.drawString(50, 680, f"Status: {order.status}")
    
    # Order Items
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 640, "Items:")
    
    y = 620
    p.setFont("Helvetica", 10)
    for item in order.items.all():
        p.drawString(70, y, f"{item.product.name} x {item.quantity} - ₹{item.product_total()}")
        y -= 20
    
    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y-20, f"Total Amount: ₹{order.total_price}")
    
    # Delivery Address
    if order.address:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y-60, "Delivery Address:")
        p.setFont("Helvetica", 10)
        p.drawString(70, y-80, f"{order.address.street_address}")
        p.drawString(70, y-100, f"{order.address.city}, {order.address.state}")
        p.drawString(70, y-120, f"PIN: {order.address.pin_code}")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'
    response.write(pdf)
    
    return response

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RepairRequest
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def accept_repair_request(request, request_id):
    if request.method == 'POST':
        try:
            repair_request = get_object_or_404(RepairRequest, id=request_id)
            
            # Update the status to 'approved'
            repair_request.status = 'approved'
            repair_request.save()
            
            messages.success(request, 'Repair request accepted successfully.')
            return redirect('tech_dashboard')
        
        except Exception as e:
            messages.error(request, f'Error accepting repair request: {str(e)}')
            return redirect('tech_dashboard')
    
    return redirect('tech_dashboard')

@login_required
def delete_repair_request(request, request_id):
    if request.method == 'POST':
        try:
            repair_request = get_object_or_404(RepairRequest, id=request_id)
            
            # Delete the repair request
            repair_request.delete()
            
            messages.success(request, 'Repair request deleted successfully.')
            return redirect('tech_dashboard')
        
        except Exception as e:
            messages.error(request, f'Error deleting repair request: {str(e)}')
            return redirect('tech_dashboard')
    
    return redirect('tech_dashboard')
def complete_repair_request(request, request_id):
    if request.method == 'POST':
        repair_request = RepairRequest.objects.get(id=request_id)
        repair_request.status = 'completed'
        repair_request.save()
        messages.success(request, 'Repair request has been marked as completed.')
        return redirect('tech_dashboard')

@login_required
def user_manage(request):
    users = User.objects.all()
    return render(request, 'user_manage.html', {'users': users})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DeliveryBoy

def deliveryboy_management(request):
    deliveryboys = DeliveryBoy.objects.all()
    return render(request, 'deliveryboy_management.html', {'deliveryboys': deliveryboys})

def add_deliveryboy(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        pin_number = request.POST.get('pin')
        
        try:
            DeliveryBoy.objects.create(
                name=name,
                email=email,
                pin_number=pin_number
            )
            messages.success(request, 'Delivery Boy added successfully!')
            return redirect('deliveryboy_management')
        except Exception as e:
            messages.error(request, f'Error adding delivery boy: {str(e)}')
    
    return render(request, 'add_deliveryboy.html')   

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DeliveryBoy

def deliveryboy_management(request):
    if request.method == 'POST':
        deliveryboy_id = request.POST.get('deliveryboy_id')
        if deliveryboy_id:
            try:
                deliveryboy = DeliveryBoy.objects.get(id=deliveryboy_id)
                deliveryboy.delete()
                messages.success(request, 'Delivery Boy deleted successfully!')
            except DeliveryBoy.DoesNotExist:
                messages.error(request, 'Delivery Boy not found!')
            return redirect('deliveryboy_management')

    deliveryboys = DeliveryBoy.objects.all()
    return render(request, 'deliveryboy_management.html', {'deliveryboys': deliveryboys})

def add_deliveryboy(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        pin_number = request.POST.get('pin')
        
        try:
            DeliveryBoy.objects.create(
                name=name,
                email=email,
                pin_number=pin_number
            )
            messages.success(request, 'Delivery Boy added successfully!')
            return redirect('deliveryboy_management')
        except Exception as e:
            messages.error(request, f'Error adding delivery boy: {str(e)}')
            return redirect('add_deliveryboy')
    
    return render(request, 'add_deliveryboy.html')

def delete_deliveryboy(request, id):
    try:
        deliveryboy = DeliveryBoy.objects.get(id=id)
        deliveryboy.delete()
        messages.success(request, 'Delivery Boy deleted successfully!')
    except DeliveryBoy.DoesNotExist:
        messages.error(request, 'Delivery Boy not found!')
    return redirect('deliveryboy_management') 

from django.shortcuts import render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import Product
from PIL import Image
import numpy as np
from scipy.spatial.distance import cosine
import os

def image_search(request):
    """
    View function for handling image-based product search
    """
    if request.method == 'POST' and request.FILES.get('search_image'):
        try:
            # Get uploaded image
            image_file = request.FILES['search_image']
            fs = FileSystemStorage()
            
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join('media', 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save uploaded image temporarily
            filename = fs.save(os.path.join('temp', image_file.name), image_file)
            uploaded_file_path = fs.path(filename)
            
            # Load and process search image
            search_img = Image.open(uploaded_file_path)
            search_img = search_img.convert('RGB')
            search_img = search_img.resize((224, 224))
            search_array = np.array(search_img).flatten() / 255.0

            # Get all products
            products = Product.objects.all()
            similar_products = []
            
            # Set similarity thresholds
            SIMILARITY_THRESHOLD = 0.80  # Lowered threshold for better matching
            
            # Track maximum similarity for this search
            max_similarity = 0

            # Compare with each product
            for product in products:
                if product.image and os.path.exists(product.image.path):
                    try:
                        # Process product image
                        product_img = Image.open(product.image.path)
                        product_img = product_img.convert('RGB')
                        product_img = product_img.resize((224, 224))
                        product_array = np.array(product_img).flatten() / 255.0

                        # Calculate similarity
                        similarity = 1 - cosine(search_array, product_array)
                        max_similarity = max(max_similarity, similarity)
                        
                        # Add products that meet the similarity threshold
                        if similarity >= SIMILARITY_THRESHOLD:
                            similar_products.append((product, similarity))
                            print(f"Found similar product: {product.name} with similarity: {similarity}")  # Debug print
                    except Exception as e:
                        print(f"Error processing product {product.id}: {str(e)}")  # Debug print
                        continue

            # Clean up temporary file
            fs.delete(filename)

            # Debug prints
            print(f"Max similarity found: {max_similarity}")
            print(f"Number of similar products found: {len(similar_products)}")

            # Sort products by similarity and get top 6
            similar_products.sort(key=lambda x: x[1], reverse=True)
            recommended_products = [p[0] for p in similar_products[:6]]

            if not recommended_products:
                messages.info(request, 'No similar products found. Please try uploading a different image.')
                return render(request, 'image_search.html', {
                    'show_results': True,
                    'products': [],
                    'title': 'Search Results'
                })

            # Debug print
            print(f"Returning {len(recommended_products)} recommended products")

            return render(request, 'image_search.html', {
                'products': recommended_products,
                'show_results': True,
                'title': 'Search Results'
            })

        except Exception as e:
            print(f"Error in image search: {str(e)}")  # Debug print
            messages.error(request, f'An error occurred while processing your image: {str(e)}')
            return render(request, 'image_search.html', {
                'title': 'Search by Image',
                'error': str(e)
            })

    # GET request - show search form
    return render(request, 'image_search.html', {
        'title': 'Search by Image'
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    
    print(f"Order status: {order.delivery_status}")  # Debug print
    print(f"Current OTP: {order.delivery_otp}")      # Debug print
    
    if order.delivery_status == 'accepted' and not order.delivery_otp:
        import random
        order.delivery_otp = str(random.randint(100000, 999999))
        order.save()
        print(f"Generated new OTP: {order.delivery_otp}")  # Debug print
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'order_detail.html', context)
