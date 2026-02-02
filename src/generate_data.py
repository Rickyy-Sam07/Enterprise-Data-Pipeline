import pandas as pd
import random
import os
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

fake = Faker('en_IN')

def generate_sales_data():
    regions = ['North', 'South', 'East', 'West', 'Central']
    products = [
        'Tomato Ketchup 500g', 'Chili Sauce 250g', 'Soy Sauce 200ml',
        'Chicken Biryani Ready Meal', 'Paneer Curry Ready Meal', 'Dal Tadka Ready Meal',
        'Paneer 200g', 'Milk 1L', 'Yogurt 500g', 'Cheese Spread 100g',
        'Potato Chips 50g', 'Namkeen Mix 100g', 'Biscuits 200g',
        'Mango Juice 1L', 'Cola 500ml', 'Water Bottle 1L'
    ]
    
    data = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(4000):  # Reduced from 5000 to 4000
        order_date = start_date + timedelta(days=random.randint(0, 365))
        
        # Intentional data quality issues
        if random.random() < 0.05:  # 5% missing dates
            order_date = None
        elif random.random() < 0.03:  # 3% wrong format dates
            order_date = "invalid_date"
        
        order_id = f"ORD{i+1:06d}"
        if random.random() < 0.02:  # 2% duplicate order IDs
            order_id = f"ORD{random.randint(1, i):06d}"
        
        quantity = random.randint(1, 50)
        if random.random() < 0.01:  # 1% negative quantities
            quantity = -random.randint(1, 10)
        
        unit_price = round(random.uniform(10, 500), 2)
        revenue = quantity * unit_price
        if random.random() < 0.015:  # 1.5% negative revenue
            revenue = -abs(revenue)
        
        region = random.choice(regions)
        if random.random() < 0.02:  # 2% invalid regions
            region = None
        
        product = random.choice(products)
        
        data.append({
            'order_id': order_id,
            'order_date': order_date,
            'region': region,
            'product': product,
            'quantity': quantity,
            'revenue': revenue
        })
    
    df = pd.DataFrame(data)
    
    # Get the project root directory (parent of src)
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, 'data', 'raw', 'sales_data.csv')
    
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} sales records with intentional quality issues")
    print(f"Data saved to: {output_path}")

if __name__ == "__main__":
    generate_sales_data()