# signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import UserProfile

# # Automatically create UserProfile when a new User is created
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# # Automatically save UserProfile whenever the User is saved
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductImageFeature
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io

@receiver(post_save, sender=Product)
def extract_product_features(sender, instance, created, **kwargs):
    if instance.image:
        # Load and preprocess image
        img = Image.open(instance.image)
        img = img.convert('RGB')
        img = img.resize((224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Extract features
        model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        features = model.predict(img_array)

        # Save features
        product_feature, _ = ProductImageFeature.objects.get_or_create(product=instance)
        product_feature.set_features(features)
        product_feature.save()
