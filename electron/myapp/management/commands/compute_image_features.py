from django.core.management.base import BaseCommand
from myapp.models import Product, ProductImage
from myapp.utils.image_processor import ImageProcessor

class Command(BaseCommand):
    help = 'Compute and store image features for all products'

    def handle(self, *args, **options):
        processor = ImageProcessor()
        products = Product.objects.all()
        
        for product in products:
            try:
                # Get or create ProductImage
                product_image, created = ProductImage.objects.get_or_create(
                    product=product
                )
                
                # Extract features
                features = processor.extract_features(product.image)
                
                # Store features
                product_image.image_features = features.tobytes()
                product_image.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Computed features for {product.name}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing {product.name}: {str(e)}'
                    )
                ) 