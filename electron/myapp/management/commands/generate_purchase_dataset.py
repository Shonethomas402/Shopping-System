from django.core.management.base import BaseCommand
from myapp.models import Order, Product
import pandas as pd
import numpy as np
import random
import os

class Command(BaseCommand):
    help = 'Generates purchase probability dataset'

    def handle(self, *args, **options):
        self.stdout.write('Generating purchase probability dataset...')
        
        try:
            # Get all products
            products = Product.objects.all()
            
            # Create records for each product
            data = []
            for product in products:
                # Get product orders
                product_orders = Order.objects.filter(
                    orderitem__product=product,
                    status='Completed'
                )
                
                record = {
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_category': product.category.name,
                    'product_price': float(product.price),
                    'wishlist_count': random.randint(0, 10),  # Replace with actual data if available
                    'cart_count': random.randint(0, 5),       # Replace with actual data if available
                    'order_count': product_orders.count(),
                }
                data.append(record)

            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create datasets directory if it doesn't exist
            dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets')
            os.makedirs(dataset_dir, exist_ok=True)
            
            # Save to CSV
            csv_path = os.path.join(dataset_dir, 'purchase_probability_dataset.csv')
            df.to_csv(csv_path, index=False)
            
            self.stdout.write(self.style.SUCCESS(f'Dataset saved to {csv_path}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating dataset: {str(e)}')) 