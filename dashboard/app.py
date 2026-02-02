import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import DatabaseManager
from sqlalchemy import text

class SalesAnalyticsDashboard:
    def __init__(self):
        self.db = DatabaseManager()
        # Check if we should use mock data - safely handle missing attribute
        try:
            self.use_mock_data = not self.db.connection_available
        except AttributeError:
            # Test actual connection
            try:
                engine = self.db.get_engine()
                with engine.connect() as conn:
                    conn.execute(text('SELECT 1'))
                self.use_mock_data = False
            except:
                self.use_mock_data = True
        
        if self.use_mock_data:
            self.mock_data = self._generate_mock_data()
        
    def run_dashboard(self):
        st.set_page_config(
            page_title="Enterprise Sales Analytics Pipeline",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("Enterprise Sales Analytics Pipeline with Data Controls")
        st.markdown("**Enterprise-Grade Data Pipeline with Validation, Exception Management & Audit Logging**")
        
        # Show connection status
        if self.use_mock_data:
            st.warning("⚠️ Database connection unavailable. Showing demo data for preview purposes.")
        
        # Sidebar for pipeline controls and run selection
        self._render_sidebar()
        
        # Dataset preview section
        self._render_dataset_preview()
        
        # Main dashboard tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Sales Analytics", 
            "Data Quality", 
            "Exceptions", 
            "Audit Trail",
            "Controls Summary"
        ])
        
        with tab1:
            self._render_sales_analytics()
        
        with tab2:
            self._render_data_quality()
        
        with tab3:
            self._render_exceptions()
        
        with tab4:
            self._render_audit_trail()
        
        with tab5:
            self._render_controls_summary()
    
    def _render_sidebar(self):
        st.sidebar.header("Pipeline Controls")
        
        # Run selection
        st.sidebar.subheader("Select Pipeline Run")
        
        # Get available runs
        runs = self._get_available_runs()
        
        if runs:
            selected_run = st.sidebar.selectbox(
                "Available Runs:",
                options=[r['run_id'] for r in runs],
                format_func=lambda x: f"{x} ({self._get_run_timestamp(x)})"
            )
            st.session_state['selected_run'] = selected_run
        else:
            st.sidebar.warning("No pipeline runs found. Please run the pipeline first.")
            st.session_state['selected_run'] = None
        
        # Pipeline status
        if st.session_state.get('selected_run'):
            status = self._get_pipeline_status(st.session_state['selected_run'])
            if status:
                latest_status = status[0]
                if latest_status['event_type'] == 'PIPELINE_END':
                    st.sidebar.success("Pipeline Completed")
                else:
                    st.sidebar.info("Pipeline Running")
    
    def _render_sales_analytics(self):
        if not st.session_state.get('selected_run'):
            st.warning("Please select a pipeline run from the sidebar.")
            return
        
        run_id = st.session_state['selected_run']
        
        # Get analytics data
        analytics_data = self._get_analytics_data(run_id)
        clean_sales = self._get_clean_sales_data(run_id)
        
        # Always show analytics section, even with zero data
        if not analytics_data:
            st.warning("No analytics data generated for this run. This may indicate a pipeline failure.")
            # Create empty analytics for display
            analytics_data = [{
                'run_id': run_id,
                'total_revenue': 0,
                'total_orders': 0,
                'region': 'ALL',
                'product': 'ALL'
            }]
        
        # Key metrics (always show, even if zero)
        col1, col2, col3, col4 = st.columns(4)
        
        total_revenue = sum([a['total_revenue'] for a in analytics_data if a['region'] == 'ALL' and a['product'] == 'ALL']) or 0
        total_orders = sum([a['total_orders'] for a in analytics_data if a['region'] == 'ALL' and a['product'] == 'ALL']) or 0
        
        with col1:
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        
        with col2:
            st.metric("Total Orders", f"{total_orders:,}")
        
        with col3:
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            st.metric("Avg Order Value", f"₹{avg_order_value:.2f}")
        
        with col4:
            unique_products = len([a for a in analytics_data if a['region'] == 'ALL' and a['product'] != 'ALL' and a['total_revenue'] > 0])
            st.metric("Active Products", unique_products)
        
        # Regional analysis (always show, even with zero data)
        st.subheader("Regional Sales Performance")
        regional_data = [a for a in analytics_data if a['region'] != 'ALL' and a['product'] == 'ALL']
        
        if regional_data:
            df_regional = pd.DataFrame(regional_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Show chart even if all values are zero
                fig_bar = px.bar(
                    df_regional, 
                    x='region', 
                    y='total_revenue',
                    title="Revenue by Region",
                    color='total_revenue',
                    color_continuous_scale='Blues'
                )
                if df_regional['total_revenue'].sum() == 0:
                    fig_bar.add_annotation(
                        text="No revenue data available",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Show pie chart even with zero data
                if df_regional['total_revenue'].sum() > 0:
                    fig_pie = px.pie(
                        df_regional, 
                        values='total_revenue', 
                        names='region',
                        title="Revenue Distribution by Region"
                    )
                else:
                    # Create equal distribution pie for zero data
                    fig_pie = px.pie(
                        df_regional, 
                        values=[1]*len(df_regional), 
                        names='region',
                        title="Regional Structure (No Revenue Data)"
                    )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No regional data available for this pipeline run.")
        
        # Product analysis
        st.subheader("Product Performance")
        product_data = [a for a in analytics_data if a['region'] == 'ALL' and a['product'] != 'ALL']
        
        if product_data:
            df_products = pd.DataFrame(product_data)
            df_products = df_products.sort_values('total_revenue', ascending=False)
            
            fig_products = px.bar(
                df_products.head(10), 
                x='total_revenue', 
                y='product',
                orientation='h',
                title="Top 10 Products by Revenue",
                color='total_revenue',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_products, use_container_width=True)
        
        # Daily trends
        if clean_sales:
            st.subheader("Daily Sales Trends")
            df_clean = pd.DataFrame(clean_sales)
            df_clean['order_date'] = pd.to_datetime(df_clean['order_date'])
            
            daily_trends = df_clean.groupby('order_date')['revenue'].sum().reset_index()
            
            fig_trend = px.line(
                daily_trends, 
                x='order_date', 
                y='revenue',
                title="Daily Revenue Trend",
                markers=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)
    
    def _render_data_quality(self):
        if not st.session_state.get('selected_run'):
            st.warning("Please select a pipeline run from the sidebar.")
            return
        
        run_id = st.session_state['selected_run']
        
        # Get validation results
        validation_data = self._get_validation_results(run_id)
        
        if not validation_data:
            st.warning("No validation data available for this run.")
            return
        
        df_validation = pd.DataFrame(validation_data)
        
        # Data quality overview
        st.subheader("Data Quality Overview")
        
        total_checks = len(df_validation)
        passed_checks = len(df_validation[df_validation['status'] == 'PASSED'])
        failed_checks = total_checks - passed_checks
        quality_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Quality Score", f"{quality_score:.1f}%")
        
        with col2:
            st.metric("Total Checks", total_checks)
        
        with col3:
            st.metric("Passed", passed_checks, delta=None)
        
        with col4:
            st.metric("Failed", failed_checks, delta=None)
        
        # Validation breakdown
        st.subheader("Validation Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = df_validation['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values, 
                names=status_counts.index,
                title="Validation Status Distribution",
                color_discrete_map={'PASSED': 'green', 'FAILED': 'red'}
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Control type breakdown
            control_counts = df_validation['control_type'].value_counts()
            fig_controls = px.bar(
                x=control_counts.values,
                y=control_counts.index,
                orientation='h',
                title="Validation Checks by Control Type",
                color=control_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_controls, use_container_width=True)
        
        # Failed validations detail
        failed_validations = df_validation[df_validation['status'] == 'FAILED']
        if not failed_validations.empty:
            st.subheader("Failed Validations")
            st.dataframe(
                failed_validations[['validation_stage', 'control_type', 'failure_reason', 'timestamp']],
                use_container_width=True
            )
    
    def _render_exceptions(self):
        if not st.session_state.get('selected_run'):
            st.warning("Please select a pipeline run from the sidebar.")
            return
        
        run_id = st.session_state['selected_run']
        
        # Get exception data
        exceptions = self._get_exceptions_data(run_id)
        
        if not exceptions:
            st.success("No exceptions found for this pipeline run!")
            return
        
        df_exceptions = pd.DataFrame(exceptions)
        
        st.subheader("Exception Analysis")
        
        # Exception metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Exceptions", len(df_exceptions))
        
        with col2:
            unique_categories = df_exceptions['error_category'].nunique()
            st.metric("Error Categories", unique_categories)
        
        with col3:
            latest_exception = df_exceptions['timestamp'].max()
            st.metric("Latest Exception", latest_exception.strftime('%H:%M:%S'))
        
        # Exception breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            category_counts = df_exceptions['error_category'].value_counts()
            fig_categories = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Exceptions by Category"
            )
            st.plotly_chart(fig_categories, use_container_width=True)
        
        with col2:
            stage_counts = df_exceptions['pipeline_stage'].value_counts()
            fig_stages = px.bar(
                x=stage_counts.index,
                y=stage_counts.values,
                title="Exceptions by Pipeline Stage",
                color=stage_counts.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_stages, use_container_width=True)
        
        # Exception details
        st.subheader("Exception Details")
        st.dataframe(
            df_exceptions[['error_category', 'pipeline_stage', 'error_details', 'timestamp']],
            use_container_width=True
        )
    
    def _render_audit_trail(self):
        if not st.session_state.get('selected_run'):
            st.warning("Please select a pipeline run from the sidebar.")
            return
        
        run_id = st.session_state['selected_run']
        
        # Get audit log
        audit_log = self._get_audit_log(run_id)
        
        if not audit_log:
            st.warning("No audit log available for this run.")
            return
        
        st.subheader("Pipeline Audit Trail")
        
        df_audit = pd.DataFrame(audit_log)
        
        # Timeline visualization
        if len(df_audit) > 1:
            # Create a simple bar chart showing events over time
            fig_timeline = px.bar(
                df_audit,
                x='timestamp',
                y='event_type',
                title="Pipeline Execution Timeline",
                orientation='h',
                color='event_type',
                hover_data=['record_count', 'event_description']
            )
            fig_timeline.update_layout(height=400)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            # Fallback: simple line chart
            fig_simple = px.scatter(
                df_audit,
                x='timestamp',
                y='event_type',
                title="Pipeline Events",
                color='event_type',
                size_max=10
            )
            st.plotly_chart(fig_simple, use_container_width=True)
        
        # Detailed audit log
        st.subheader("Detailed Audit Log")
        st.dataframe(
            df_audit[['timestamp', 'event_type', 'event_description', 'record_count']],
            use_container_width=True
        )
    
    def _render_controls_summary(self):
        if not st.session_state.get('selected_run'):
            st.warning("Please select a pipeline run from the sidebar.")
            return
        
        st.subheader("Enterprise Data Controls Summary")
        
        # Control definitions
        st.markdown("""
        ### Implemented Data Controls:
        
        **1. Schema Validation**
        - ✅ Required column presence check
        - ✅ Extra column detection
        
        **2. Data Quality Controls**
        - ✅ Null value validation
        - ✅ Date format validation
        - ✅ Business rule enforcement (revenue ≥ 0, quantity > 0)
        - ✅ Reference data validation (valid regions)
        
        **3. Duplicate Detection**
        - ✅ Order ID uniqueness check
        
        **4. Exception Management**
        - ✅ Failed record isolation
        - ✅ Error categorization
        - ✅ Audit trail maintenance
        
        **5. Audit & Compliance**
        - ✅ Complete pipeline logging
        - ✅ Timestamp tracking
        - ✅ Record count validation
        - ✅ Control execution tracking
        """)
        
        # Governance metrics
        run_id = st.session_state['selected_run']
        validation_data = self._get_validation_results(run_id)
        
        if validation_data:
            df_validation = pd.DataFrame(validation_data)
            
            st.subheader("Governance Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Control Effectiveness:**")
                control_effectiveness = df_validation.groupby('control_type')['status'].apply(
                    lambda x: (x == 'PASSED').sum() / len(x) * 100
                ).round(1)
                
                for control, effectiveness in control_effectiveness.items():
                    st.write(f"• {control}: {effectiveness}%")
            
            with col2:
                st.markdown("**Data Lineage:**")
                st.write(f"• Source: data/raw/sales_data.csv")
                st.write(f"• Processing Run: {run_id}")
                st.write(f"• Target: PostgreSQL Database")
                st.write(f"• Exceptions: data/exceptions/")
                st.write(f"• Audit Logs: logs/pipeline_*.log")
    
    # Helper methods for data retrieval
    def _get_available_runs(self):
        if self.use_mock_data:
            return [{'run_id': 'demo_run_001', 'start_time': datetime.now()}]
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT DISTINCT run_id, MIN(timestamp) as start_time
                    FROM audit_log 
                    GROUP BY run_id 
                    ORDER BY start_time DESC
                """))
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _get_run_timestamp(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT MIN(timestamp) as start_time
                    FROM audit_log 
                    WHERE run_id = :run_id
                """), {'run_id': run_id})
                row = result.fetchone()
                if row and row[0]:
                    return row[0].strftime('%Y-%m-%d %H:%M')
                return "Unknown"
        except:
            return "Unknown"
    
    def _get_pipeline_status(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT event_type, event_description, record_count, timestamp
                    FROM audit_log 
                    WHERE run_id = :run_id
                    ORDER BY timestamp DESC
                """), {'run_id': run_id})
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _get_analytics_data(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM analytics_summary 
                    WHERE run_id = :run_id
                """), {'run_id': run_id})
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _get_clean_sales_data(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM clean_sales 
                    WHERE run_id = :run_id
                """), {'run_id': run_id})
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _get_validation_results(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM validation_results 
                    WHERE run_id = :run_id
                """), {'run_id': run_id})
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _get_exceptions_data(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM exceptions 
                    WHERE run_id = :run_id
                """), {'run_id': run_id})
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _get_audit_log(self, run_id):
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM audit_log 
                    WHERE run_id = :run_id
                    ORDER BY timestamp
                """), {'run_id': run_id})
                return [dict(row._mapping) for row in result]
        except:
            return []
    
    def _render_dataset_preview(self):
        """Show sample dataset and pipeline execution controls"""
        st.header("Dataset Preview & Pipeline Controls")
        
        # Show sample data from the most recent run or raw data
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Sample Sales Data")
            
            # Try to get sample from clean_sales first, then raw_sales
            sample_data = self._get_sample_data()
            
            if sample_data:
                df_sample = pd.DataFrame(sample_data)
                # Convert string columns to avoid Arrow compatibility issues
                for col in df_sample.select_dtypes(include=['object']).columns:
                    df_sample[col] = df_sample[col].astype(str)
                st.dataframe(df_sample.head(10), use_container_width=True)
                
                # Data statistics
                st.subheader("Dataset Statistics")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                
                with stats_col1:
                    st.metric("Total Records", len(df_sample))
                
                with stats_col2:
                    if 'region' in df_sample.columns:
                        st.metric("Regions", df_sample['region'].nunique())
                
                with stats_col3:
                    if 'product' in df_sample.columns:
                        st.metric("Products", df_sample['product'].nunique())
            else:
                st.info("No data available. Please generate sample data first.")
        
        with col2:
            st.subheader("Quick Actions")
            
            # Pipeline execution status
            if st.session_state.get('pipeline_running'):
                st.warning("Pipeline is running...")
                if st.button("Refresh Status"):
                    st.session_state['pipeline_running'] = False
            else:
                # Generate new data
                if st.button("Generate New Data", use_container_width=True):
                    self._run_data_generation()
                
                st.markdown("---")
                
                # Run full pipeline
                if st.button("Execute Pipeline", use_container_width=True, type="primary"):
                    self._run_full_pipeline()
                
                st.markdown("---")
                
                # Quick stats
                runs = self._get_available_runs()
                st.metric("Total Runs", len(runs))
    
    def _get_sample_data(self):
        """Get sample data for preview"""
        if self.use_mock_data:
            return self.mock_data['sales_data'][:10]
        try:
            engine = self.db.get_engine()
            with engine.connect() as conn:
                # Try clean_sales first
                result = conn.execute(text("""
                    SELECT order_id, order_date, region, product, quantity, revenue
                    FROM clean_sales 
                    ORDER BY processed_timestamp DESC 
                    LIMIT 100
                """))
                data = [dict(row._mapping) for row in result]
                
                if not data:
                    # Fallback to raw_sales
                    result = conn.execute(text("""
                        SELECT order_id, order_date, region, product, quantity, revenue
                        FROM raw_sales 
                        ORDER BY ingestion_timestamp DESC 
                        LIMIT 100
                    """))
                    data = [dict(row._mapping) for row in result]
                
                return data
        except:
            return []
    
    def _run_data_generation(self):
        """Execute data generation script with progress tracking"""
        try:
            import subprocess
            import sys
            import os
            import threading
            import time
            
            # Create progress placeholder
            progress_placeholder = st.empty()
            
            def run_script():
                script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'generate_data.py')
                result = subprocess.run([
                    sys.executable, script_path
                ], capture_output=True, text=True)
                return result
            
            # Show progress while running
            progress_placeholder.info("🔄 Generating sample data...")
            
            # Run in thread to avoid blocking
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_script)
                
                # Show progress animation
                progress_steps = ["Generating data.", "Generating data..", "Generating data..."]
                step = 0
                
                while not future.done():
                    progress_placeholder.info(progress_steps[step % 3])
                    step += 1
                    time.sleep(0.5)
                
                result = future.result()
            
            progress_placeholder.empty()
            
            if result.returncode == 0:
                st.success("✅ Data generation completed successfully!")
                return True
            else:
                st.error(f"❌ Data generation failed: {result.stderr}")
                return False
        except Exception as e:
            st.error(f"Error generating data: {str(e)}")
            return False
    
    def _run_full_pipeline(self):
        """Execute the full pipeline with progress tracking"""
        try:
            import subprocess
            import sys
            import os
            import threading
            import time
            
            # Create progress components
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def run_pipeline():
                script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'pipeline.py')
                result = subprocess.run([
                    sys.executable, script_path
                ], capture_output=True, text=True)
                return result
            
            # Set pipeline running state
            st.session_state['pipeline_running'] = True
            
            # Pipeline stages for progress tracking
            stages = [
                "Initializing pipeline...",
                "Creating database tables...",
                "Ingesting raw data...",
                "Running validations...",
                "Processing exceptions...",
                "Transforming data...",
                "Generating analytics...",
                "Finalizing pipeline..."
            ]
            
            # Run pipeline in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_pipeline)
                
                # Simulate progress (since we can't track actual pipeline progress)
                stage_idx = 0
                progress = 0
                
                while not future.done():
                    if stage_idx < len(stages):
                        status_text.text(stages[stage_idx])
                        progress = min(90, (stage_idx + 1) * 12)  # Max 90% until completion
                        progress_bar.progress(progress)
                        stage_idx += 1
                    
                    time.sleep(2)  # Update every 2 seconds
                
                result = future.result()
            
            st.session_state['pipeline_running'] = False
            
            # Complete progress
            progress_bar.progress(100)
            status_text.text("Pipeline completed!")
            
            # Clear progress after 2 seconds
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            
            if result.returncode == 0:
                st.success("✅ Pipeline executed successfully!")
                st.balloons()  # Celebration animation
                return True
            else:
                st.error(f"❌ Pipeline failed: {result.stderr}")
                return False
        except Exception as e:
            st.error(f"Error running pipeline: {str(e)}")
            st.session_state['pipeline_running'] = False
            return False
    
    def _generate_mock_data(self):
        """Generate mock data for demo purposes"""
        from faker import Faker
        import random
        
        fake = Faker()
        regions = ['North', 'South', 'East', 'West', 'Central']
        products = ['Sauces & Ketchup', 'Ready-to-Eat Meals', 'Dairy Products', 'Snacks', 'Beverages']
        
        # Generate sample sales data
        sales_data = []
        for i in range(100):
            sales_data.append({
                'order_id': f'ORD{1000+i}',
                'order_date': fake.date_between(start_date='-30d', end_date='today'),
                'region': random.choice(regions),
                'product': random.choice(products),
                'quantity': random.randint(1, 50),
                'revenue': round(random.uniform(100, 5000), 2)
            })
        
        return {
            'sales_data': sales_data,
            'analytics': {
                'total_revenue': sum(s['revenue'] for s in sales_data),
                'total_orders': len(sales_data),
                'regions': len(regions),
                'products': len(products)
            },
            'validation_results': [
                {'control_type': 'Schema Validation', 'status': 'PASSED'},
                {'control_type': 'Business Rules', 'status': 'PASSED'},
                {'control_type': 'Data Quality', 'status': 'FAILED'},
                {'control_type': 'Duplicate Check', 'status': 'PASSED'}
            ],
            'exceptions': [
                {'error_category': 'DATA_QUALITY_ISSUE', 'pipeline_stage': 'VALIDATION', 'error_details': 'Missing date field'}
            ]
        }

if __name__ == "__main__":
    dashboard = SalesAnalyticsDashboard()
    dashboard.run_dashboard()