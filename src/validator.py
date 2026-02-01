import pandas as pd
import os
from datetime import datetime
from database import DatabaseManager
from sqlalchemy import text
import json

class DataValidator:
    def __init__(self, run_id, audit_logger):
        self.run_id = run_id
        self.db = DatabaseManager()
        self.audit_logger = audit_logger
        self.validation_results = []
        
    def validate_schema(self, df):
        """Schema validation - check for required columns"""
        required_columns = ['order_id', 'order_date', 'region', 'product', 'quantity', 'revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self._log_validation_failure(
                0, "SCHEMA_VALIDATION", "MISSING_COLUMNS", 
                f"Missing columns: {missing_columns}"
            )
            return False
        
        extra_columns = [col for col in df.columns if col not in required_columns]
        if extra_columns:
            self.audit_logger.logger.warning(f"Extra columns found: {extra_columns}")
        
        return True
    
    def validate_records(self, df):
        """Validate individual records against business rules"""
        valid_records = []
        invalid_records = []
        
        for idx, row in df.iterrows():
            record_valid = True
            
            # Null value checks
            if pd.isna(row['order_id']) or row['order_id'] == '':
                self._log_validation_failure(idx, "NULL_CHECK", "MISSING_ORDER_ID", "Order ID is null or empty")
                record_valid = False
            
            if pd.isna(row['region']) or row['region'] == '':
                self._log_validation_failure(idx, "NULL_CHECK", "MISSING_REGION", "Region is null or empty")
                record_valid = False
            
            # Date format validation
            if not self._validate_date(row['order_date'], idx):
                record_valid = False
            
            # Business rule validations
            if pd.notna(row['revenue']) and row['revenue'] < 0:
                self._log_validation_failure(idx, "BUSINESS_RULE", "NEGATIVE_REVENUE", f"Revenue is negative: {row['revenue']}")
                record_valid = False
            
            if pd.notna(row['quantity']) and row['quantity'] <= 0:
                self._log_validation_failure(idx, "BUSINESS_RULE", "INVALID_QUANTITY", f"Quantity is zero or negative: {row['quantity']}")
                record_valid = False
            
            # Region validation
            valid_regions = ['North', 'South', 'East', 'West', 'Central']
            if pd.notna(row['region']) and row['region'] not in valid_regions:
                self._log_validation_failure(idx, "BUSINESS_RULE", "INVALID_REGION", f"Invalid region: {row['region']}")
                record_valid = False
            
            if record_valid:
                self._log_validation_success(idx, "RECORD_VALIDATION", "PASSED")
                valid_records.append(row)
            else:
                invalid_records.append(row)
        
        return pd.DataFrame(valid_records), pd.DataFrame(invalid_records)
    
    def check_duplicates(self, df):
        """Check for duplicate order IDs"""
        duplicates = df[df.duplicated(subset=['order_id'], keep=False)]
        
        for idx, row in duplicates.iterrows():
            self._log_validation_failure(
                idx, "DUPLICATE_CHECK", "DUPLICATE_ORDER_ID", 
                f"Duplicate order ID: {row['order_id']}"
            )
        
        return df.drop_duplicates(subset=['order_id'], keep='first')
    
    def _validate_date(self, date_value, record_idx):
        """Validate date format"""
        if pd.isna(date_value):
            self._log_validation_failure(record_idx, "DATE_VALIDATION", "MISSING_DATE", "Order date is missing")
            return False
        
        if isinstance(date_value, str) and date_value == "invalid_date":
            self._log_validation_failure(record_idx, "DATE_VALIDATION", "INVALID_FORMAT", f"Invalid date format: {date_value}")
            return False
        
        try:
            if isinstance(date_value, str):
                pd.to_datetime(date_value)
            return True
        except:
            self._log_validation_failure(record_idx, "DATE_VALIDATION", "PARSE_ERROR", f"Cannot parse date: {date_value}")
            return False
    
    def _log_validation_failure(self, record_id, stage, control_type, reason):
        """Log validation failure to database"""
        self.validation_results.append({
            'record_id': record_id,
            'stage': stage,
            'control_type': control_type,
            'status': 'FAILED',
            'reason': reason
        })
    
    def _log_validation_success(self, record_id, stage, control_type):
        """Log validation success to database"""
        self.validation_results.append({
            'record_id': record_id,
            'stage': stage,
            'control_type': control_type,
            'status': 'PASSED',
            'reason': None
        })
    
    def save_validation_results(self):
        """Save all validation results to database"""
        if not self.validation_results:
            return
        
        engine = self.db.get_engine()
        with engine.connect() as conn:
            for result in self.validation_results:
                conn.execute(text("""
                    INSERT INTO validation_results 
                    (run_id, record_id, validation_stage, control_type, status, failure_reason, timestamp)
                    VALUES (:run_id, :record_id, :stage, :control_type, :status, :reason, :timestamp)
                """), {
                    'run_id': self.run_id,
                    'record_id': result['record_id'],
                    'stage': result['stage'],
                    'control_type': result['control_type'],
                    'status': result['status'],
                    'reason': result['reason'],
                    'timestamp': datetime.now()
                })
            conn.commit()
    
    def generate_validation_summary(self):
        """Generate validation summary metrics"""
        total_checks = len(self.validation_results)
        failed_checks = len([r for r in self.validation_results if r['status'] == 'FAILED'])
        passed_checks = total_checks - failed_checks
        
        failure_percentage = (failed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Group failures by control type
        failure_breakdown = {}
        for result in self.validation_results:
            if result['status'] == 'FAILED':
                control_type = result['control_type']
                failure_breakdown[control_type] = failure_breakdown.get(control_type, 0) + 1
        
        summary = {
            'run_id': self.run_id,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'failure_percentage': round(failure_percentage, 2),
            'failure_breakdown': failure_breakdown,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save summary to CSV
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processed_dir = os.path.join(project_root, 'data', 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        
        summary_df = pd.DataFrame([summary])
        summary_file = os.path.join(processed_dir, 'validation_summary.csv')
        summary_df.to_csv(summary_file, index=False)
        
        return summary