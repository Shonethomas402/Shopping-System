from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User





class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)



class Category(models.Model):
    name = models.CharField(max_length=100)



    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    def __str__(self):
        
        return self.name
    

class Cart(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())
class CartItem(models.Model):
     cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
     product = models.ForeignKey(Product, on_delete=models.CASCADE)
     quantity = models.PositiveIntegerField(default=1)

     def product_total(self):
        return self.product.price * self.quantity
    

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, product_id):
    # Fetch the product by its ID
    product = get_object_or_404(Product, id=product_id)
    
    # Pass the product to the template for rendering
    context = {
        'product': product,
    }
    return render(request, 'product_detail.html', context)

from django.db import models
from django.contrib.auth.models import User

class DeliveryAddress(models.Model):  # Renamed from Address to DeliveryAddress
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    house_no = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    place = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name}, {self.address}"

