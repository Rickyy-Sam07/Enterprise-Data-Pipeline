import pandas as pd
from datetime import datetime
from database import DatabaseManager
from sqlalchemy import text

class DataTransformer:
    def __init__(self, run_id, audit_logger):
        self.run_id = run_id
        self.db = DatabaseManager()
        self.audit_logger = audit_logger
    
    def transform_clean_data(self, clean_df):
        """Transform validated data for analytics"""
        if clean_df.empty:
            self.audit_logger.logger.warning("No clean data to transform")
            return pd.DataFrame()
        
        transformed_df = clean_df.copy()
        
        # Standardize date formats
        transformed_df['order_date'] = pd.to_datetime(transformed_df['order_date']).dt.date
        
        # Normalize region names (already clean, but ensure consistency)
        region_mapping = {
            'north': 'North', 'south': 'South', 'east': 'East', 
            'west': 'West', 'central': 'Central'
        }
        transformed_df['region'] = transformed_df['region'].str.title()
        
        # Derive business metrics
        transformed_df['revenue_per_unit'] = (
            transformed_df['revenue'] / transformed_df['quantity']
        ).round(2)
        
        # Add processing metadata
        transformed_df['run_id'] = self.run_id
        transformed_df['processed_timestamp'] = datetime.now()
        
        # Save to database
        self._save_clean_data(transformed_df)
        
        # Generate analytics summaries
        self._generate_analytics_summaries(transformed_df)
        
        self.audit_logger.log_transformation(len(transformed_df))
        
        return transformed_df
    
    def _save_clean_data(self, df):
        """Save clean transformed data to database"""
        engine = self.db.get_engine()
        
        # Clear existing data for this run
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM clean_sales WHERE run_id = :run_id"), 
                        {'run_id': self.run_id})
            conn.commit()
        
        # Insert new clean data
        df.to_sql('clean_sales', engine, if_exists='append', index=False)
        
        self.audit_logger.logger.info(f"Saved {len(df)} clean records to database")
    
    def _generate_analytics_summaries(self, df):
        """Generate pre-calculated analytics summaries"""
        summaries = []
        
        # Overall summary
        total_summary = {
            'run_id': self.run_id,
            'total_revenue': df['revenue'].sum(),
            'total_orders': len(df),
            'region': 'ALL',
            'product': 'ALL',
            'daily_sales': df['revenue'].sum(),
            'calculation_date': datetime.now().date(),
            'created_timestamp': datetime.now()
        }
        summaries.append(total_summary)
        
        # Regional summaries
        regional_summary = df.groupby('region').agg({
            'revenue': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        for _, row in regional_summary.iterrows():
            summary = {
                'run_id': self.run_id,
                'total_revenue': row['revenue'],
                'total_orders': row['order_id'],
                'region': row['region'],
                'product': 'ALL',
                'daily_sales': row['revenue'],
                'calculation_date': datetime.now().date(),
                'created_timestamp': datetime.now()
            }
            summaries.append(summary)
        
        # Product summaries
        product_summary = df.groupby('product').agg({
            'revenue': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        for _, row in product_summary.iterrows():
            summary = {
                'run_id': self.run_id,
                'total_revenue': row['revenue'],
                'total_orders': row['order_id'],
                'region': 'ALL',
                'product': row['product'],
                'daily_sales': row['revenue'],
                'calculation_date': datetime.now().date(),
                'created_timestamp': datetime.now()
            }
            summaries.append(summary)
        
        # Daily summaries
        daily_summary = df.groupby('order_date').agg({
            'revenue': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        for _, row in daily_summary.iterrows():
            summary = {
                'run_id': self.run_id,
                'total_revenue': row['revenue'],
                'total_orders': row['order_id'],
                'region': 'ALL',
                'product': 'ALL',
                'daily_sales': row['revenue'],
                'calculation_date': row['order_date'],
                'created_timestamp': datetime.now()
            }
            summaries.append(summary)
        
        # Save summaries to database
        engine = self.db.get_engine()
        
        # Clear existing summaries for this run
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM analytics_summary WHERE run_id = :run_id"), 
                        {'run_id': self.run_id})
            conn.commit()
        
        # Insert new summaries
        summary_df = pd.DataFrame(summaries)
        summary_df.to_sql('analytics_summary', engine, if_exists='append', index=False)
        
        self.audit_logger.logger.info(f"Generated {len(summaries)} analytics summaries")
    
    def get_analytics_data(self):
        """Retrieve analytics data for reporting"""
        engine = self.db.get_engine()
        
        with engine.connect() as conn:
            # Get latest run data
            result = conn.execute(text("""
                SELECT * FROM analytics_summary 
                WHERE run_id = :run_id
                ORDER BY created_timestamp DESC
            """), {'run_id': self.run_id})
            
            analytics_data = [dict(row._mapping) for row in result]
            return analytics_data