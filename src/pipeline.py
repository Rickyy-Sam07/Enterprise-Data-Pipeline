import pandas as pd
import uuid
import os
from datetime import datetime
from database import DatabaseManager
from audit_logger import AuditLogger
from validator import DataValidator
from exception_handler import ExceptionHandler
from transformer import DataTransformer
from sqlalchemy import text

class SalesDataPipeline:
    def __init__(self):
        self.run_id = str(uuid.uuid4())[:8]
        self.audit_logger = AuditLogger(self.run_id)
        self.db = DatabaseManager()
        
    def run_pipeline(self, source_file=None):
        """Execute the complete enterprise data pipeline"""
        if source_file is None:
            # Get the project root directory (parent of src)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            source_file = os.path.join(project_root, 'data', 'raw', 'sales_data.csv')
        try:
            self.audit_logger.log_pipeline_start()
            
            # Step 1: Data Ingestion
            raw_df = self._ingest_data(source_file)
            
            # Step 2: Data Validation
            validator = DataValidator(self.run_id, self.audit_logger)
            clean_df, invalid_df = self._validate_data(validator, raw_df)
            
            # Step 3: Exception Handling
            exception_handler = ExceptionHandler(self.run_id, self.audit_logger)
            exception_handler.handle_exceptions(invalid_df)
            
            # Step 4: Data Transformation
            transformer = DataTransformer(self.run_id, self.audit_logger)
            final_df = transformer.transform_clean_data(clean_df)
            
            # Step 5: Always Generate Basic Analytics (even if no clean data)
            self._generate_basic_analytics(raw_df, clean_df, invalid_df)
            
            # Step 6: Generate Final Reports
            validation_summary = validator.generate_validation_summary()
            
            self.audit_logger.log_pipeline_end(len(raw_df))
            
            return {
                'run_id': self.run_id,
                'total_records': len(raw_df),
                'clean_records': len(clean_df),
                'invalid_records': len(invalid_df),
                'validation_summary': validation_summary,
                'status': 'SUCCESS'
            }
            
        except Exception as e:
            self.audit_logger.log_exception(str(e))
            
            # Always generate basic analytics even on failure
            try:
                raw_df = pd.read_csv(source_file) if os.path.exists(source_file) else pd.DataFrame()
                self._generate_basic_analytics(raw_df, pd.DataFrame(), pd.DataFrame())
            except:
                pass  # If even basic analytics fail, continue
            
            return {
                'run_id': self.run_id,
                'status': 'FAILED',
                'error': str(e)
            }
    
    def _ingest_data(self, source_file):
        """Controlled data ingestion with metadata"""
        try:
            # Read raw data
            df = pd.read_csv(source_file)
            
            # Add ingestion metadata
            df['run_id'] = self.run_id
            df['ingestion_timestamp'] = datetime.now()
            df['source_name'] = source_file
            
            # Store raw data in database
            engine = self.db.get_engine()
            df.to_sql('raw_sales', engine, if_exists='append', index=False)
            
            self.audit_logger.log_ingestion(len(df), source_file)
            
            # Return original columns only for processing
            original_columns = ['order_id', 'order_date', 'region', 'product', 'quantity', 'revenue']
            return df[original_columns]
            
        except Exception as e:
            self.audit_logger.log_exception(f"Data ingestion failed: {str(e)}")
            raise
    
    def _validate_data(self, validator, df):
        """Execute comprehensive data validation"""
        try:
            # Schema validation
            if not validator.validate_schema(df):
                raise Exception("Schema validation failed")
            
            # Record-level validation
            clean_df, invalid_df = validator.validate_records(df)
            
            # Duplicate check
            clean_df = validator.check_duplicates(clean_df)
            
            # Save validation results
            validator.save_validation_results()
            
            self.audit_logger.log_validation_summary(len(clean_df), len(invalid_df))
            
            return clean_df, invalid_df
            
        except Exception as e:
            self.audit_logger.log_exception(f"Data validation failed: {str(e)}")
            raise
    
    def get_pipeline_status(self):
        """Get current pipeline execution status"""
        engine = self.db.get_engine()
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT event_type, event_description, record_count, timestamp
                FROM audit_log 
                WHERE run_id = :run_id
                ORDER BY timestamp DESC
            """), {'run_id': self.run_id})
            
            status_log = [dict(row._mapping) for row in result]
            return status_log
    
    def get_validation_report(self):
        """Generate comprehensive validation report"""
        engine = self.db.get_engine()
        
        with engine.connect() as conn:
            # Get validation summary
            result = conn.execute(text("""
                SELECT 
                    control_type,
                    status,
                    COUNT(*) as count
                FROM validation_results 
                WHERE run_id = :run_id
                GROUP BY control_type, status
                ORDER BY control_type, status
            """), {'run_id': self.run_id})
            
            validation_report = [dict(row._mapping) for row in result]
            return validation_report
    
    def _generate_basic_analytics(self, raw_df, clean_df, invalid_df):
        """Generate basic analytics summaries even when pipeline fails"""
        engine = self.db.get_engine()
        
        # Clear existing summaries for this run
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM analytics_summary WHERE run_id = :run_id"), 
                        {'run_id': self.run_id})
            conn.commit()
        
        summaries = []
        current_date = datetime.now().date()
        
        # Always create an overall summary (even if zero)
        total_summary = {
            'run_id': self.run_id,
            'total_revenue': float(clean_df['revenue'].sum()) if not clean_df.empty else 0.0,
            'total_orders': len(clean_df) if not clean_df.empty else 0,
            'region': 'ALL',
            'product': 'ALL',
            'daily_sales': float(clean_df['revenue'].sum()) if not clean_df.empty else 0.0,
            'calculation_date': current_date,
            'created_timestamp': datetime.now()
        }
        summaries.append(total_summary)
        
        # Generate regional summaries (even if zero)
        regions = ['North', 'South', 'East', 'West', 'Central']
        for region in regions:
            if not clean_df.empty:
                region_data = clean_df[clean_df['region'] == region]
                revenue = float(region_data['revenue'].sum()) if not region_data.empty else 0.0
                orders = len(region_data) if not region_data.empty else 0
            else:
                revenue = 0.0
                orders = 0
            
            summary = {
                'run_id': self.run_id,
                'total_revenue': revenue,
                'total_orders': orders,
                'region': region,
                'product': 'ALL',
                'daily_sales': revenue,
                'calculation_date': current_date,
                'created_timestamp': datetime.now()
            }
            summaries.append(summary)
        
        # Generate product summaries (even if zero)
        products = ['Tomato Ketchup 500g', 'Chicken Biryani Ready Meal', 'Paneer 200g', 
                   'Potato Chips 50g', 'Mango Juice 1L']
        for product in products:
            if not clean_df.empty:
                product_data = clean_df[clean_df['product'].str.contains(product.split()[0], na=False)]
                revenue = float(product_data['revenue'].sum()) if not product_data.empty else 0.0
                orders = len(product_data) if not product_data.empty else 0
            else:
                revenue = 0.0
                orders = 0
            
            summary = {
                'run_id': self.run_id,
                'total_revenue': revenue,
                'total_orders': orders,
                'region': 'ALL',
                'product': product,
                'daily_sales': revenue,
                'calculation_date': current_date,
                'created_timestamp': datetime.now()
            }
            summaries.append(summary)
        
        # Save summaries to database
        if summaries:
            summary_df = pd.DataFrame(summaries)
            summary_df.to_sql('analytics_summary', engine, if_exists='append', index=False)
            self.audit_logger.logger.info(f"Generated {len(summaries)} basic analytics summaries")

if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    db.create_database()
    db.create_tables()
    
    # Run pipeline
    pipeline = SalesDataPipeline()
    result = pipeline.run_pipeline()
    
    print(f"Pipeline execution completed:")
    print(f"Run ID: {result['run_id']}")
    print(f"Status: {result['status']}")
    if result['status'] == 'SUCCESS':
        print(f"Total records: {result['total_records']}")
        print(f"Clean records: {result['clean_records']}")
        print(f"Invalid records: {result['invalid_records']}")
        print(f"Data quality: {(result['clean_records']/result['total_records']*100):.1f}%")