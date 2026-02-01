import logging
import os
from datetime import datetime
from database import DatabaseManager
from sqlalchemy import text

class AuditLogger:
    def __init__(self, run_id):
        self.run_id = run_id
        self.db = DatabaseManager()
        self.setup_file_logging()
    
    def setup_file_logging(self):
        # Create logs directory if it doesn't exist
        import os
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_pipeline_start(self):
        message = f"Pipeline started - Run ID: {self.run_id}"
        self.logger.info(message)
        self._log_to_db("PIPELINE_START", message, 0)
    
    def log_pipeline_end(self, total_records):
        message = f"Pipeline completed - Run ID: {self.run_id}, Total records: {total_records}"
        self.logger.info(message)
        self._log_to_db("PIPELINE_END", message, total_records)
    
    def log_ingestion(self, record_count, source_file):
        message = f"Data ingested from {source_file} - {record_count} records"
        self.logger.info(message)
        self._log_to_db("DATA_INGESTION", message, record_count)
    
    def log_validation_summary(self, passed_count, failed_count):
        message = f"Validation completed - Passed: {passed_count}, Failed: {failed_count}"
        self.logger.info(message)
        self._log_to_db("VALIDATION_SUMMARY", message, passed_count + failed_count)
    
    def log_transformation(self, record_count):
        message = f"Data transformation completed - {record_count} records processed"
        self.logger.info(message)
        self._log_to_db("DATA_TRANSFORMATION", message, record_count)
    
    def log_exception(self, error_message, record_count=0):
        message = f"Exception occurred: {error_message}"
        self.logger.error(message)
        self._log_to_db("SYSTEM_ERROR", message, record_count)
    
    def _log_to_db(self, event_type, description, record_count):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO audit_log (run_id, event_type, event_description, record_count, timestamp)
                    VALUES (:run_id, :event_type, :description, :record_count, :timestamp)
                """), {
                    'run_id': self.run_id,
                    'event_type': event_type,
                    'description': description,
                    'record_count': record_count,
                    'timestamp': datetime.now()
                })
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log to database: {e}")