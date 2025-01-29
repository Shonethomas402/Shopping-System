from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator





class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.ForeignKey('DeliveryAddress', on_delete=models.SET_NULL, null=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def product_total(self):
        return self.product.price * self.quantity




from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ensure category names are unique

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  related_name='products')
def __str__(self):
        
         return self.name

  

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Add this field to track active carts

    # def total_price(self):
    #     return sum(item.product.price * item.quantity for item in self.items.all())



class CartItems(models.Model):

     cart = models.ForeignKey('Cart', related_name='items', on_delete=models.CASCADE)
     product = models.ForeignKey('Product', on_delete=models.CASCADE)
     quantity = models.PositiveIntegerField(default=1)
     def product_total(self):
         return self.product.price * self.quantity

    #  def __str__(self):
    #      return f"{self.cart.user.username} - {self.product.name}"


class SavedForLaterItem(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      product = models.ForeignKey(Product, on_delete=models.CASCADE)
      saved_date = models.DateTimeField(auto_now_add=True)




class DeliveryAddress(models.Model):  # Renamed from Address to DeliveryAddress
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    house_no = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    place = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name}, {self.address}"

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     location = models.CharField(max_length=15)
#     phone_no = models.CharField(max_length=10)

#     def __str__(self):
#         return f'{self.user.username} Profile'
    
# models.py
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blocked = models.BooleanField(default=False)

    def __str__(self):
         return self.user.username
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Note: If you're using 'rating' instead of 'score'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

class RepairMaster(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=191, unique=True, db_index=True)
    phone = models.CharField(max_length=15)
    id_no = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['email'], name='email_idx'),
        ]

    def __str__(self):
        return self.name
    
class Technician(models.Model):
    name = models.CharField(max_length=30)
    pin_no = models.CharField(max_length=20, unique=True)
    repair_master = models.ForeignKey(RepairMaster, on_delete=models.CASCADE, related_name='technicians')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class RepairRequest(models.Model):
    DEVICE_CHOICES = [
        ('smartphone', 'Smartphone'),
        ('laptop', 'Laptop'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES
    )

    proof_of_purchase = models.FileField(
        upload_to='repair_proofs/',
        validators=[FileExtensionValidator(['pdf'])]
    )

    issue_description = models.TextField()

    pin_number = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_type} - PIN: {self.pin_number}"