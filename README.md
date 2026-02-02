# Enterprise Sales Analytics Pipeline with Data Controls
## link:https://enterprise-data-pipeline-sambhranta.streamlit.app/
## 🏢 Project Overview

**Enterprise-Grade Data Pipeline with Validation, Exception Management & Audit Logging**

This enterprise data pipeline demonstrates production-ready data processing with comprehensive controls, validation, exception handling, and audit logging for sales performance analytics in the Indian market.

## 🎯 Business Use Case

**Sales Performance Analytics** - Answering critical business questions:
- What is total & regional sales performance?
- Which products drive revenue across Indian regions?
- How much data is unreliable due to quality issues?
- What exceptions need business attention?

## 🏗️ Architecture

```
Raw Data → Ingestion → Validation → Exception Handling → Transformation → Analytics
    ↓           ↓           ↓              ↓               ↓            ↓
Database    Audit Log   Controls    Exception Store   Clean Data   Dashboard
```

## 📊 Data Sources

**Sample Sales Data (5,000 records)**
- **Regions**: North, South, East, West, Central (Indian business regions)
- **Products**: Sauces & Ketchup, Ready-to-Eat Meals, Dairy Products, Snacks, Beverages
- **Time Range**: Last 12 months (rolling)
- **Intentional Quality Issues**: Missing dates, duplicate IDs, negative revenue, format errors

## 🔧 Technical Stack

- **Database**: PostgreSQL
- **Backend**: Python 3.x
- **Dashboard**: Streamlit
- **Data Processing**: Pandas, SQLAlchemy
- **Visualization**: Plotly
- **Environment**: Python venv

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- PostgreSQL 12+
- Git

### Setup Instructions

1. **Clone and Setup**
   ```bash
   cd "c:\sambhranta\projects\Enterprise Data Pipeline"
   setup.bat
   ```

2. **Configure Database**
   - Update `.env` file with your PostgreSQL credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=sales_analytics
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

3. **Run Pipeline**
   ```bash
   run_pipeline.bat
   ```

4. **Start Dashboard**
   ```bash
   start_dashboard.bat
   ```

## 📁 Project Structure

```
Enterprise Data Pipeline/
├── data/
│   ├── raw/                 # Raw sales data with quality issues
│   ├── processed/           # Validation summaries
│   └── exceptions/          # Failed records with audit trail
├── logs/                    # Pipeline execution logs
├── src/                     # Core pipeline components
│   ├── generate_data.py     # Sample data generator
│   ├── database.py          # Database connection & setup
│   ├── audit_logger.py      # Enterprise audit logging
│   ├── validator.py         # Data validation & controls
│   ├── exception_handler.py # Exception management
│   ├── transformer.py       # Data transformation
│   └── pipeline.py          # Main orchestrator
├── dashboard/
│   └── app.py              # Streamlit analytics dashboard
├── requirements.txt         # Python dependencies
├── .env                    # Database configuration
└── *.bat                   # Windows execution scripts
```

## 🎯 Data Controls & Validation

### Schema Validation
- ✅ Required column presence check
- ✅ Extra column detection
- ✅ Data type validation

### Data Quality Controls
- ✅ Null value validation
- ✅ Date format validation
- ✅ Business rules enforcement:
  - Revenue ≥ 0
  - Quantity > 0
  - Valid Indian regions
- ✅ Duplicate detection (Order ID uniqueness)

### Exception Management
- ✅ Failed record isolation
- ✅ Error categorization:
  - MISSING_REQUIRED_FIELD
  - BUSINESS_RULE_VIOLATION
  - DATA_FORMAT_ERROR
  - DATA_QUALITY_ISSUE
- ✅ Complete audit trail
- ✅ Exception trend analysis

## 📋 Audit & Compliance Features

### Comprehensive Logging
- **Pipeline Events**: Start/end timestamps, record counts
- **Validation Results**: Detailed control execution logs
- **System Errors**: Exception tracking with stack traces
- **Data Lineage**: Complete data flow documentation

### Audit Trail Components
- **Run ID**: Unique identifier for each pipeline execution
- **Timestamps**: Precise timing for all operations
- **Record Counts**: Validation at each pipeline stage
- **Control Results**: Pass/fail status for all validations

## 📊 Analytics Dashboard

### Sales Performance
- **Total Revenue**: ₹X,XXX,XXX across all regions
- **Regional Analysis**: Performance by North, South, East, West, Central
- **Product Performance**: Revenue by category and SKU
- **Daily Trends**: Time-series analysis of sales patterns

### Data Quality Monitoring
- **Quality Score**: Overall data health percentage
- **Validation Breakdown**: Control-wise pass/fail analysis
- **Exception Trends**: Error patterns over time
- **Control Effectiveness**: Governance metrics

### Exception Dashboard
- **Exception Categories**: Breakdown by error type
- **Pipeline Stage Analysis**: Where failures occur
- **Trend Analysis**: Exception patterns over time
- **Detailed Investigation**: Drill-down into failed records

## 🔍 Key Differentiators (Enterprise-Ready)

### Enterprise-Grade Features
1. **Controlled Data Entry**: Structured ingestion with metadata
2. **Comprehensive Validation**: Multi-layer data quality checks
3. **Exception Management**: No data deletion, full traceability
4. **Audit Logging**: Complete pipeline execution history
5. **Governance Reporting**: Control effectiveness metrics
6. **Data Lineage**: End-to-end data flow documentation

### Compliance & Governance
- **Auditable**: Every operation is logged and traceable
- **Recoverable**: Failed records are preserved with context
- **Reportable**: Comprehensive dashboards for stakeholders
- **Scalable**: Modular architecture for enterprise deployment

## 🎯 Business Value

### For Business Users
- **Sales Insights**: Regional and product performance analysis
- **Data Trust**: Quality scores and validation reporting
- **Exception Visibility**: Clear view of data issues requiring attention

### For Data Teams
- **Quality Monitoring**: Automated data validation and reporting
- **Exception Management**: Systematic handling of data issues
- **Audit Compliance**: Complete pipeline execution history

### for IT/Governance
- **Control Framework**: Comprehensive data validation controls
- **Audit Trail**: Complete operational history
- **Risk Management**: Proactive data quality monitoring

## 🚀 Deployment Considerations

### Production Readiness
- **Database**: Migrate to production PostgreSQL cluster
- **Scheduling**: Integrate with enterprise job scheduler
- **Monitoring**: Add alerting for pipeline failures
- **Security**: Implement proper authentication and authorization

### Scalability
- **Data Volume**: Designed to handle enterprise data volumes
- **Parallel Processing**: Can be extended for distributed processing
- **API Integration**: Ready for REST API wrapper
- **Cloud Deployment**: Compatible with AWS/Azure/GCP

## 📈 Success Metrics

### Data Quality
- **Quality Score**: >95% validation pass rate
- **Exception Rate**: <5% failed records
- **Processing Time**: <30 minutes for 100K records

### Business Impact
- **Decision Speed**: Faster sales performance insights
- **Data Trust**: Increased confidence in analytics
- **Compliance**: 100% audit trail coverage

---

**Built for Enterprise Data Teams | Enterprise-Grade Data Pipeline**

*This project demonstrates production-ready data engineering with enterprise controls, making it suitable for corporate data teams and governance requirements.*
