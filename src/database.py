import os
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import streamlit as st

load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Try Streamlit secrets first, then environment variables
        if hasattr(st, 'secrets') and 'database' in st.secrets:
            self.host = st.secrets.database.DB_HOST
            self.port = st.secrets.database.DB_PORT
            self.database = st.secrets.database.DB_NAME
            self.user = st.secrets.database.DB_USER
            self.password = st.secrets.database.DB_PASSWORD
        else:
            self.host = os.getenv('DB_HOST', 'localhost')
            self.port = os.getenv('DB_PORT', '5432')
            self.database = os.getenv('DB_NAME', 'postgres')
            self.user = os.getenv('DB_USER', 'postgres')
            self.password = os.getenv('DB_PASSWORD', '')
        
    def get_engine(self):
        connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return create_engine(connection_string)
    
    def create_database(self):
        # Supabase already provides the database, so we skip database creation
        print(f"Using Supabase database: {self.database}")
        print("Note: Supabase provides the database automatically")
    
    def create_tables(self):
        engine = self.get_engine()
        
        tables_sql = """
        CREATE TABLE IF NOT EXISTS raw_sales (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50),
            ingestion_timestamp TIMESTAMP,
            source_name VARCHAR(100),
            order_id VARCHAR(50),
            order_date VARCHAR(50),
            region VARCHAR(50),
            product VARCHAR(200),
            quantity INTEGER,
            revenue DECIMAL(10,2)
        );
        
        CREATE TABLE IF NOT EXISTS validation_results (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50),
            record_id INTEGER,
            validation_stage VARCHAR(100),
            control_type VARCHAR(100),
            status VARCHAR(20),
            failure_reason VARCHAR(500),
            timestamp TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS clean_sales (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50),
            order_id VARCHAR(50),
            order_date DATE,
            region VARCHAR(50),
            product VARCHAR(200),
            quantity INTEGER,
            revenue DECIMAL(10,2),
            revenue_per_unit DECIMAL(10,2),
            processed_timestamp TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS exceptions (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50),
            original_record_id INTEGER,
            error_category VARCHAR(100),
            pipeline_stage VARCHAR(100),
            error_details TEXT,
            timestamp TIMESTAMP,
            raw_data JSONB
        );
        
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50),
            event_type VARCHAR(100),
            event_description TEXT,
            record_count INTEGER,
            timestamp TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS analytics_summary (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(50),
            total_revenue DECIMAL(15,2),
            total_orders INTEGER,
            region VARCHAR(50),
            product VARCHAR(200),
            daily_sales DECIMAL(15,2),
            calculation_date DATE,
            created_timestamp TIMESTAMP
        );
        """
        
        with engine.connect() as conn:
            conn.execute(text(tables_sql))
            conn.commit()
        
        print("Database tables created successfully")

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_database()
    db.create_tables()