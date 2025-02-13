import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)

# Number of records to generate
n_records = 1000

# Generate data
data = {
    'order_id': [f'ORD{str(i).zfill(6)}' for i in range(1, n_records + 1)],
    'user_id': [f'USR{str(random.randint(1000, 9999))}' for _ in range(n_records)],
}

# Fixed warehouse location for Kottayam
fixed_warehouse = 'Kottayam Depot'
fixed_warehouse_pin = '686001'

# Kottayam delivery locations
kottayam_warehouses = {
    'Kottayam Central': '686001',
    'Ettumanoor Hub': '686631',
    'Changanassery Warehouse': '686101',
    'Pala Storage': '686575',
    'Vaikom Depot': '686141',
    'Mundakayam Center': '686513',
    'Kanjirappally Hub': '686507',
    'Ponkunnam Warehouse': '686506',
    'Erumely Depot': '686509',
    'Ranni Storage': '689672'
}

# Generate random order placement times within the last 6 months
end_date = datetime.now()
start_date = end_date - timedelta(days=180)
order_times = [start_date + timedelta(
    seconds=random.randint(0, int((end_date - start_date).total_seconds()))
) for _ in range(n_records)]
data['order_placement_time'] = order_times

# Assign fixed warehouse location and pin code
data['warehouse_location'] = [fixed_warehouse] * n_records
data['warehouse_pin_code'] = [fixed_warehouse_pin] * n_records

# Generate delivery locations based on the new Kottayam warehouses
delivery_cities = list(kottayam_warehouses.keys())  # Using Kottayam warehouses as delivery locations
data['delivery_location'] = [
    random.choice(delivery_cities) for _ in range(n_records)
]
data['delivery_pin_code'] = [
    kottayam_warehouses[loc] for loc in data['delivery_location']
]

# Calculate distances (in km) based on random distribution
data['distance'] = [
    round(random.uniform(5, 1500), 2) for _ in range(n_records)
]

# Assign shipping methods
data['shipping_method'] = np.random.choice(
    ['Standard', 'Express'],
    size=n_records,
    p=[0.7, 0.3]  # 70% Standard, 30% Express
)

# Calculate delivery times based on shipping method, distance and order placement time
def calculate_delivery_time(row):
    base_time = row['distance'] / 300  # Assume 300km per day average speed
    
    # Get order time directly
    order_time = row['order_placement_time']
    
    # Calculate delivery days based on shipping method
    if row['shipping_method'] == 'Express':
        delivery_time_days = min(3, max(1, round(base_time * 0.6)))  # 40% faster than standard
    else:
        delivery_time_days = min(7, max(1, round(base_time)))
    
    # Add delivery days and set delivery time between 9 AM and 5 PM
    delivery_hour = random.randint(9, 17)
    delivery_minute = random.choice([0, 15, 30, 45])
    
    # Calculate actual delivery datetime
    delivery_datetime = order_time + timedelta(days=delivery_time_days)
    delivery_datetime = delivery_datetime.replace(
        hour=delivery_hour,
        minute=delivery_minute,
        second=0,
        microsecond=0
    )
    
    # Format the predicted delivery time to match order_placement_time format
    formatted_time = delivery_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
    
    return delivery_time_days, formatted_time

# Create DataFrame
df = pd.DataFrame(data)
df['delivery_time'], df['predicted_delivery_time'] = zip(*df.apply(calculate_delivery_time, axis=1))

# Create a directory for the dataset if it doesn't exist
dataset_dir = os.path.join(os.path.dirname(__file__), 'datasets')
os.makedirs(dataset_dir, exist_ok=True)

# Save to CSV in the datasets directory
csv_path = os.path.join(dataset_dir, 'delivery_time_dataset.csv')
df.to_csv(csv_path, index=False)

print(f"\nDataset saved to: {csv_path}")

# Display first few rows and dataset info
print("\nFirst few rows of the dataset:")
print(df.head())
print("\nDataset Info:")
print(df.info())

# Display some basic statistics
print("\nBasic Statistics:")
print(df.describe())

# Display shipping method distribution
print("\nShipping Method Distribution:")
print(df['shipping_method'].value_counts(normalize=True))

# Display average delivery times by shipping method
print("\nAverage Delivery Times by Shipping Method:")
print(df.groupby('shipping_method')['delivery_time'].value_counts()) 