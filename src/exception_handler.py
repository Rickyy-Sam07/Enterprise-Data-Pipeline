import pandas as pd
import json
import os
from datetime import datetime
from database import DatabaseManager
from sqlalchemy import text

class ExceptionHandler:
    def __init__(self, run_id, audit_logger):
        self.run_id = run_id
        self.db = DatabaseManager()
        self.audit_logger = audit_logger
    
    def handle_exceptions(self, invalid_records, pipeline_stage="VALIDATION"):
        """Process and store failed records with full audit trail"""
        if invalid_records.empty:
            return
        
        exception_data = []
        
        for idx, record in invalid_records.iterrows():
            # Categorize the error
            error_category = self._categorize_error(record)
            
            # Create exception record
            exception_record = {
                'run_id': self.run_id,
                'original_record_id': idx,
                'error_category': error_category,
                'pipeline_stage': pipeline_stage,
                'error_details': self._generate_error_details(record),
                'timestamp': datetime.now(),
                'raw_data': record.to_dict()
            }
            
            exception_data.append(exception_record)
        
        # Save to database
        self._save_exceptions_to_db(exception_data)
        
        # Save to CSV for analysis
        self._save_exceptions_to_csv(exception_data)
        
        self.audit_logger.logger.info(f"Processed {len(exception_data)} exception records")
    
    def _categorize_error(self, record):
        """Categorize the type of error for reporting"""
        if pd.isna(record.get('order_id')) or record.get('order_id') == '':
            return "MISSING_REQUIRED_FIELD"
        elif pd.notna(record.get('revenue')) and record['revenue'] < 0:
            return "BUSINESS_RULE_VIOLATION"
        elif pd.isna(record.get('order_date')) or record.get('order_date') == 'invalid_date':
            return "DATA_FORMAT_ERROR"
        elif pd.notna(record.get('quantity')) and record['quantity'] <= 0:
            return "BUSINESS_RULE_VIOLATION"
        else:
            return "DATA_QUALITY_ISSUE"
    
    def _generate_error_details(self, record):
        """Generate detailed error description"""
        errors = []
        
        if pd.isna(record.get('order_id')) or record.get('order_id') == '':
            errors.append("Missing order ID")
        
        if pd.isna(record.get('region')) or record.get('region') == '':
            errors.append("Missing region")
        
        if pd.isna(record.get('order_date')):
            errors.append("Missing order date")
        elif record.get('order_date') == 'invalid_date':
            errors.append("Invalid date format")
        
        if pd.notna(record.get('revenue')) and record['revenue'] < 0:
            errors.append(f"Negative revenue: {record['revenue']}")
        
        if pd.notna(record.get('quantity')) and record['quantity'] <= 0:
            errors.append(f"Invalid quantity: {record['quantity']}")
        
        valid_regions = ['North', 'South', 'East', 'West', 'Central']
        if pd.notna(record.get('region')) and record['region'] not in valid_regions:
            errors.append(f"Invalid region: {record['region']}")
        
        return "; ".join(errors) if errors else "Unknown error"
    
    def _save_exceptions_to_db(self, exception_data):
        """Save exception records to database"""
        engine = self.db.get_engine()
        
        with engine.connect() as conn:
            for exc in exception_data:
                # Convert NaN values to None for JSON serialization
                raw_data_clean = {}
                for key, value in exc['raw_data'].items():
                    if pd.isna(value):
                        raw_data_clean[key] = None
                    else:
                        raw_data_clean[key] = value
                
                conn.execute(text("""
                    INSERT INTO exceptions 
                    (run_id, original_record_id, error_category, pipeline_stage, error_details, timestamp, raw_data)
                    VALUES (:run_id, :record_id, :category, :stage, :details, :timestamp, :raw_data)
                """), {
                    'run_id': exc['run_id'],
                    'record_id': exc['original_record_id'],
                    'category': exc['error_category'],
                    'stage': exc['pipeline_stage'],
                    'details': exc['error_details'],
                    'timestamp': exc['timestamp'],
                    'raw_data': json.dumps(raw_data_clean, default=str)
                })
            conn.commit()
    
    def _save_exceptions_to_csv(self, exception_data):
        """Save exception records to CSV for analysis"""
        if not exception_data:
            return
        
        # Create exceptions directory if it doesn't exist
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exceptions_dir = os.path.join(project_root, 'data', 'exceptions')
        os.makedirs(exceptions_dir, exist_ok=True)
        
        # Flatten the data for CSV
        csv_data = []
        for exc in exception_data:
            flat_record = {
                'run_id': exc['run_id'],
                'original_record_id': exc['original_record_id'],
                'error_category': exc['error_category'],
                'pipeline_stage': exc['pipeline_stage'],
                'error_details': exc['error_details'],
                'timestamp': exc['timestamp']
            }
            # Add original record data, handling NaN values
            for key, value in exc['raw_data'].items():
                if pd.isna(value):
                    flat_record[key] = None
                else:
                    flat_record[key] = value
            csv_data.append(flat_record)
        
        df = pd.DataFrame(csv_data)
        filename = os.path.join(exceptions_dir, f"exceptions_{self.run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(filename, index=False)
        
        self.audit_logger.logger.info(f"Exception records saved to {filename}")
    
    def get_exception_trends(self):
        """Generate exception trend analysis"""
        engine = self.db.get_engine()
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    error_category,
                    COUNT(*) as error_count,
                    DATE(timestamp) as error_date
                FROM exceptions 
                WHERE run_id = :run_id
                GROUP BY error_category, DATE(timestamp)
                ORDER BY error_date DESC, error_count DESC
            """), {'run_id': self.run_id})
            
            trends = [dict(row._mapping) for row in result]
            return trends