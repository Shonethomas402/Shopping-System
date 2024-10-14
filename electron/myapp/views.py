from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import *
#from .models import Cart

# Home view

# class ProductListView(ListView):
#     model = Product
#     template_name = 'product_list.html'
#     context_object_name = 'products'

def home(request):
    products = Product.objects.all()
    context = {
        'products': products,
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
                  return redirect('dashboard')  # Redirect to user dashboard after login
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    logout()
    request.session.clear()
    return redirect('login')

def cart(request):
    return render(request, 'cart.html')  # You'll need a cart template

def profile(request):
    return render(request, 'profile.html')  # You'll need a profile template

def search(request):
    query = request.GET.get('query')
    # Process the search query
    return render(request, 'search.html', {'query': query})  # You'll need a search template

def user_dashboard(request, category=None):
    if request.user.is_authenticated:
        query = request.GET.get('query')
        if query:
            products = Product.objects.filter(name__icontains=query)  # Case-insensitive search for products
            category_name = f"Search Results for '{query}'"
        elif category:
            products = Product.objects.filter(category__name=category)
            category_name = category
        else:
            products = Product.objects.all()
            category_name = "All"
        orders = Order.objects.filter(user=request.user)
        context = {
            'products': products,
            'orders': orders,
            'category_name': category_name,
        }
        return render(request, 'user_dashboard.html', context)
    else:
        return redirect('login')


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



def category_management(request):
    return render(request, 'category_management.html')

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

def subscribe_newsletter(request):
    # Logic to subscribe to the newsletter
    return render(request, 'newsletter_subscribe.html')

def add_to_cart(request, product_id):
     product = get_object_or_404(Product, id=product_id)

     # Get the user's carts
     carts = Cart.objects.filter(user=request.user)

     # Check if the user has more than one cart
     if carts.exists():
         cart = carts.first()  # You can decide how to handle multiple carts (here just taking the first one)
     else:
         # Create a new cart if none exists
         cart = Cart.objects.create(user=request.user)

     # Get or create the cart item
     cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
     if not created:
         cart_item.quantity += 1  # Increment quantity if already exists
     cart_item.save()  # Save the cart item

     return redirect('view_cart')





def view_cart(request):
    # Fetch the first cart associated with the user, or create a new one if none exists
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart:
        # Optionally create a new cart if the user has none
        cart = Cart.objects.create(user=request.user)
    
    cart_items = CartItem.objects.filter(cart=cart)

    products_in_cart = []
    total_price = 0

    for cart_item in cart_items:
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
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    # Delete the cart item
    cart_item.delete()
    
    # Redirect to the view cart page
    return redirect('view_cart')

def checkout(request):
    # Get the user's cart; if multiple exist, get the first one
    cart = Cart.objects.filter(user=request.user).first()

    if cart is None:
        # Optionally handle the case where the user has no cart
        return render(request, 'checkout.html', {'error': 'No cart found.'})
    
    # Get all items in the cart
    cart_items = CartItem.objects.filter(cart=cart)

    products_in_cart = []
    total_price = 0

    # Loop through each cart item to retrieve product details and calculate totals
    for cart_item in cart_items:
        product = cart_item.product  # Retrieve the product from the cart item
        product_total = product.price * cart_item.quantity  # Calculate total for this product
        products_in_cart.append({
            'product': product,
            'quantity': cart_item.quantity,
            'product_total': product_total
        })
        total_price += product_total  # Update total price

    if request.method == 'POST':
        # Handle payment logic here
        return redirect('payment_success')

    context = {
        'cart_items': products_in_cart,
        'total_price': total_price,
    }
    
    return render(request, 'checkout.html', context)

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)  # Logs out the user
    return redirect('home')


from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem

def increase_quantity(request, product_id):
    # Get the user's cart
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart:
        return redirect('view_cart')

    # Get the cart item for the specified product
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    # Increase the quantity
    cart_item.quantity += 1
    cart_item.save()

    return redirect('view_cart')


def decrease_quantity(request, product_id):
    # Get the user's cart
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart:
        return redirect('view_cart')

    # Get the cart item for the specified product
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

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
