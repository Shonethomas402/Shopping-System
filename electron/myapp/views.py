from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.decorators import login_required
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

from django.http import JsonResponse
from django.shortcuts import render
from .models import Order
from django.shortcuts import get_object_or_404, redirect
from .models import Cart, Product


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
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if user.is_superuser:  # If user is admin
                    return redirect('admin_dashboard')  # Admin dashboard
                else:
                  return redirect('user_dashboard')  # Redirect to user dashboard after login
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

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
from .models import SavedForLaterItem
@login_required
def view_saved_items(request):
    saved_items = SavedForLaterItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'saved_for_later.html', {'saved_items': saved_items})
def remove_saved_items(request, item_id):
    item = get_object_or_404(SavedForLaterItem, pk=item_id)
    if request.method == "POST":
        item.delete()
    return redirect('view_saved_items')
def profile(request):
    return render(request, 'profile.html')  # You'll need a profile template

def search(request):
    query = request.GET.get('query')
    # Process the search query
    return render(request, 'search.html', {'query': query})  # You'll need a search template

from django.shortcuts import render, redirect
from .models import Product, Category  # Ensure you import necessary models
from .forms import UserLoginForm  # Assuming you have a form for login

def user_dashboard(request):
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
 # Ensure only admin users can access this view
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    return render(request, 'admin_dashboard.html')

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

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

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

def order_management(request):
    return render(request, 'order_management.html')

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
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItems.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1  # Increment quantity if item already in cart
        cart_item.save()
    
    return redirect('cart')

def view_cart(request):
     # Fetch the first cart associated with the user, or create a new one if none exists
     cart = Cart.objects.filter(user=request.user).first()
    
     if not cart:
         # Optionally create a new cart if the user has none
         cart = Cart.objects.create(user=request.user)
    
     cart_items = CartItems.objects.filter(cart=cart)
    

     products_in_cart = []
     total_price = 0

     for cart_item in cart_items:
         available_quantity = min(cart_item.quantity, cart_item.product.stock)

        
         product_total = cart_item.product.price * cart_item.quantity
         products_in_cart.append({
             'product': cart_item.product,
             'quantity': cart_item.quantity,
             'product_total': product_total
         })
         total_price += product_total

     context = {
         'products_in_cart': products_in_cart,
         'total_price': total_price,
         
     }

     return render(request, 'cart.html', context)





def remove_from_cart(request, product_id):
    # Fetch all carts for the user
    carts = Cart.objects.filter(user=request.user)

    # If multiple carts exist, just get the first one (or handle according to your logic)
    if carts.exists():
        cart = carts.first()  # Get the first cart
    else:
        return redirect('view_cart')  # Redirect if no cart found

    # Get the cart item to remove
    cart_item = get_object_or_404(CartItems, cart=cart, product_id=product_id)

    # Delete the cart item
    cart_item.delete()
    
    # Redirect to the view cart page
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
    logout(request)  # Logs out the user
    return redirect('home')


from django.shortcuts import render, redirect, get_object_or_404



def increase_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.filter(user=request.user).first()
    cart_item = get_object_or_404(CartItems, cart=cart, product=product)

    # Check if adding one more exceeds the stock
    if cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')



def decrease_quantity(request, product_id):
    # Get the user's cart
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart:
        return redirect('view_cart')

    # Get the cart item for the specified product
    cart_item = get_object_or_404(CartItems, cart=cart, product_id=product_id)

    # Decrease the quantity
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        # Optionally remove the item if quantity reaches 1 and user tries to decrease further
        cart_item.delete()

    return redirect('view_cart')

from django.shortcuts import render


def orders(request):
    # Logic for fetching and displaying user orders can go here
    return render(request, 'orders.html')
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

def delivery_address_list(request):
    addresses = DeliveryAddress.objects.filter(user=request.user)
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        request.session['selected_address'] = selected_address_id
        return redirect('confirm_order')
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
from .forms import ProfileUpdateForm

@login_required
def update_profile(request):
     # Get the profile associated with the current user
     profile = request.user.profile

     if request.method == 'POST':
         form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)
         if form.is_valid():
             form.save()  # This will save both the User's email and Profile fields
             return redirect('profile')
     else:
         form = ProfileUpdateForm(instance=profile, user=request.user)
     return render(request, 'update_profile.html', {'form': form})

# views.py


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
        if not re.match(r'^[A-Za-z\s]+$', category_name):
            messages.error(request, 'Category name must contain only letters and spaces.')
            return redirect('category_management')

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

@login_required
def checkout(request):
    if request.method == 'POST':
        return redirect('delivery_address_list')
    cart_items = CartItems.objects.filter(cart__user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})


from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import razorpay

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

@login_required
def confirm_order(request):
    cart_items = CartItems.objects.filter(cart__user=request.user)
    selected_address_id = request.session.get('selected_address')
    
    # Calculate total price in paise for Razorpay
    total_price = sum(item.product.price * item.quantity for item in cart_items) * 100  
    
    # Create Razorpay Order
    try:
        payment_order = client.order.create({
            'amount': float(total_price),
            'currency': 'INR',
            'payment_capture': 1
        })
    except razorpay.errors.BadRequestError as e:
        # Handle error gracefully if Razorpay order creation fails
        return render(request, 'error.html', {'message': 'Error creating payment order'})

    # Create Order instance
    order = Order.objects.create(
        user=request.user,
        address_id=selected_address_id,
        total_price=total_price / 100,  # Save as the original amount (not in paise)
        status='Pending',
        payment_id=payment_order['id']
    )

    # Add items to OrderItem
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    # Clear selected address from session after order creation
    request.session.pop('selected_address', None)

    # Pass data to template
    context = {
        'order': order,
        'cart_items': cart_items,
        'payment_order_id': payment_order['id'],
        'razorpay_key': settings.RAZORPAY_API_KEY,
    }
    return render(request, 'payment.html', context)

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import razorpay
import logging

# Configure logging
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def payment_response(request):
    if request.method == 'POST':
        # Retrieve necessary Razorpay payment data
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        if not all([payment_id, order_id, signature]):
            logger.error("Missing payment information from Razorpay response.")
            return redirect('payment_failure')

        try:
            # Verify the payment signature
            params = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params)
            logger.info("Payment signature verified successfully.")

            # Retrieve and update order status to 'Completed'
            order = get_object_or_404(Order, order_id=order_id)
            order.status = 'Completed'
            order.save()
            logger.info(f"Order {order.id} status updated to 'Completed'.")

            # Clear the user's cart items
            CartItems.objects.filter(cart__user=request.user).delete()
            logger.info("Cart cleared after successful payment.")

            return redirect('payment_success')

        except razorpay.errors.SignatureVerificationError as e:
            logger.error(f"Signature verification failed: {e}")
            return redirect('payment_failure')

        except Order.DoesNotExist:
            logger.error(f"Order with payment_id {order_id} not found.")
            return redirect('payment_failure')

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return redirect('payment_failure')
    
    # If method is not POST, redirect to home or an error page
    return redirect('user_dashboard')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Wishlist

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, "Product added to your wishlist!")
    else:
        messages.info(request, "This product is already in your wishlist.")
    
    return redirect('view_wishlist')
def remove_from_wishlist(request, product_id):
    # Assuming you have a Wishlist model that links users to products
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product_id=product_id)
        wishlist_item.delete()  # Remove the item from the wishlist
        messages.success(request, 'Product removed from your wishlist.')
    except Wishlist.DoesNotExist:
        messages.error(request, 'No such product in your wishlist.')
    return redirect('view_wishlist')  # Change 'wishlist' to your actual wishlist URL name

# @login_required
# def view_wishlist(request):
#     # Get the products in the user's wishlist
#     wishlist_products = Product.objects.filter(wishlist__user=request.user)
#     context = {
#         'wishlist_products': wishlist_products,
#     }
#     return render(request, 'wishlist.html', context)
  
def view_wishlist(request):
    # Retrieve wishlist items for the logged-in user
    wishlist_products = Wishlist.objects.filter(user=request.user).select_related('product')
    # Pass the wishlist items to the template
    return render(request, 'wishlist.html', {'wishlist_products': wishlist_products})

