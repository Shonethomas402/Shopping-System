from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator
import numpy as np





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
    payment_id = models.CharField(max_length=91, blank=True, null=True)
    address = models.ForeignKey('DeliveryAddress', on_delete=models.SET_NULL, null=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_transit', 'In Transit'),
            ('accepted', 'Accepted'),
            ('delivered', 'Delivered')
        ],
        null=True,
        blank=True
    )
    delivery_boy = models.ForeignKey(
        'DeliveryBoy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    delivery_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_verified = models.BooleanField(default=False)
    delivery_time = models.DateTimeField(null=True, blank=True)

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
    image = models.ImageField(upload_to='product_images/', null=True, blank=True, max_length=191)
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
    name = models.CharField(max_length=15)
    house_no = models.CharField(max_length=10)
    address = models.CharField(max_length=19)
    place = models.CharField(max_length=15)
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

    
# class Technician(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician', null=True, blank=True)
#     name = models.CharField(max_length=30)
#     pin_no = models.CharField(max_length=20, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
        
#         return self.name
    
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
        ('rejected', 'Rejected'),
        ('completed', 'Completed')  # Add completed status
    ]

    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES
    )

    proof_of_purchase = models.FileField(
        upload_to='repair_proofs/',
        validators=[FileExtensionValidator(['pdf'])],
        max_length=191  # Reduced max_length to stay under MySQL's limit
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

def assign_technician(self):
        """Assign technician based on PIN number"""
        try:
            technician = Technician.objects.get(pin_number=self.pin_number)
            self.assigned_technician = technician
            self.status = 'approved'  # Auto-approve when technician is found
            self.save()
            return True
        except Technician.DoesNotExist:
            return False
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=RepairRequest)
def notify_technician(sender, instance, created, **kwargs):
    if created and instance.assigned_technician:
        # You can implement email/SMS notification here
        print(f"New repair request assigned to {instance.assigned_technician.name}")

class Technician(models.Model):
    name = models.CharField(max_length=15)
    pin_number = models.CharField(max_length=7, unique=True)  # Ensure PIN is unique
    email = models.EmailField(unique=True)  # Ensure email is unique

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    capacity = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DeliveryBoy(models.Model):
    id = models.AutoField(primary_key=True)  # Remove null=True and blank=True
    name = models.CharField(max_length=15)
    pin_number = models.CharField(max_length=7, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class ProductImageFeature(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    features = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_features(self, feature_array):
        self.features = feature_array.tobytes()

    def get_features(self):
        return np.frombuffer(self.features, dtype=np.float32)


