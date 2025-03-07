import os
import django
import sys
from django.db.models import Q

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electron.settings')
django.setup()

# Now import your models
from myapp.models import Order, Product, Wishlist, CartItems
import pandas as pd
import numpy as np
from django.db.models import Count, Avg, F
from datetime import datetime, timedelta
from django.utils import timezone

# Set random seed for reproducibility
np.random.seed(42)

def generate_purchase_probability_dataset():
    # Get all products
    products = Product.objects.all()
    
    # Get recent orders (last 30 days) for better relevance
    recent_date = timezone.now() - timedelta(days=30)
    
    # Get product statistics from orders
    product_stats = Order.objects.filter(
        status='Completed',
        created_at__gte=recent_date
    ).values(
        'items__product'
    ).annotate(
        order_count=Count('id'),
        avg_order_value=Avg('total_price'),
        category_orders=Count('items__product__category'),
        recent_orders=Count('id', filter=Q(created_at__gte=recent_date))
    ).order_by('items__product')

    data = []
    for product in products:
        # Get product's order statistics
        stats = product_stats.filter(items__product=product.id).first() or {}
        
        # Get current stock level
        stock_level = product.stock
        
        # Get wishlist count
        wishlist_count = Wishlist.objects.filter(product=product).count()
        
        # Get active cart count
        cart_count = CartItems.objects.filter(
            product=product,
            cart__is_active=True
        ).count()
        
        # Calculate price factor (compared to category average)
        category_avg_price = Product.objects.filter(
            category=product.category
        ).aggregate(Avg('price'))['price__avg'] or product.price
        
        price_factor = float(product.price) / float(category_avg_price)

        record = {
            'product_id': product.id,
            'product_name': product.name,
            'product_category': product.category.name,
            'product_price': float(product.price),
            'stock_level': stock_level,
            'wishlist_count': wishlist_count,
            'cart_count': cart_count,
            'order_count': stats.get('order_count', 0),
            'category_order_count': stats.get('category_orders', 0),
            'recent_orders': stats.get('recent_orders', 0),
            'price_factor': round(price_factor, 2)
        }
        data.append(record)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Calculate purchase probability
    def calculate_purchase_probability(row):
        # Base probability starts at 15%
        probability = 15
        
        # Price range factors
        price = row['product_price']
        category = row['product_category']
        
        # Define price ranges and their impact based on category
        price_ranges = {
            'laptop': {
                'budget': (0, 30000),
                'mid': (30000, 80000),
                'premium': (80000, float('inf'))
            },
            'phone': {
                'budget': (0, 15000),
                'mid': (15000, 40000),
                'premium': (40000, float('inf'))
            },
            'Smart TVs': {
                'budget': (0, 25000),
                'mid': (25000, 50000),
                'premium': (50000, float('inf'))
            },
            'Smartwatches': {
                'budget': (0, 2000),
                'mid': (2000, 5000),
                'premium': (5000, float('inf'))
            },
            'Cameras': {
                'budget': (0, 50000),
                'mid': (50000, 150000),
                'premium': (150000, float('inf'))
            },
            'Headphones': {
                'budget': (0, 1500),
                'mid': (1500, 5000),
                'premium': (5000, float('inf'))
            }
        }
        
        # Get price ranges for the category
        ranges = price_ranges.get(category, {
            'budget': (0, 5000),
            'mid': (5000, 20000),
            'premium': (20000, float('inf'))
        })
        
        # Calculate price factor (max 20%)
        if price <= ranges['budget'][1]:
            # Budget range - highest probability boost
            price_factor = 20
        elif price <= ranges['mid'][1]:
            # Mid range - moderate probability boost
            price_factor = 15
        else:
            # Premium range - lower probability boost for mass market
            price_factor = 10
        
        # Adjust price factor based on price_factor (comparison with category average)
        if row['price_factor'] < 1:  # If price is below category average
            price_factor += min(10, (1 - row['price_factor']) * 20)
        
        probability += price_factor
        
        # Other existing factors
        if row['stock_level'] > 0:
            stock_factor = min(10, (row['stock_level'] / 10) * 2)
            probability += stock_factor
        
        order_factor = min(25, row['order_count'] * 5)
        probability += order_factor
        
        recent_factor = min(15, row['recent_orders'] * 7.5)
        probability += recent_factor
        
        category_factor = min(10, row['category_order_count'] * 2)
        probability += category_factor
        
        interest_factor = min(15, (row['wishlist_count'] + row['cart_count']) * 3)
        probability += interest_factor
        
        # Ensure probability is between 0 and 100
        probability = max(0, min(100, probability))
        
        return round(probability, 1)

    # Calculate purchase probability for each record
    df['purchase_probability'] = df.apply(calculate_purchase_probability, axis=1)

    # Create a directory for the dataset if it doesn't exist
    dataset_dir = os.path.join(os.path.dirname(__file__), 'datasets')
    os.makedirs(dataset_dir, exist_ok=True)

    # Save to CSV in the datasets directory
    csv_path = os.path.join(dataset_dir, 'purchase_probability_dataset.csv')
    df.to_csv(csv_path, index=False)

    return df

if __name__ == "__main__":
    df = generate_purchase_probability_dataset()
    print("\nFirst few rows of the dataset:")
    print(df.head())
    print("\nDataset Info:")
    print(df.info())
    print("\nBasic Statistics:")
    print(df.describe()) 