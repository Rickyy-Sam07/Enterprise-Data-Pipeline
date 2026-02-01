# Streamlit Cloud Deployment Instructions

## Database Configuration - Neon DB (Recommended)

## Quick Setup:
1. Create account at https://neon.tech
2. Create new project
3. Copy connection details
4. Update Streamlit secrets:

```toml
[database]
DB_HOST = "your-endpoint.us-east-1.aws.neon.tech"
DB_PORT = 5432
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "your_password"
```

## Why Neon DB?
- ✅ Better Streamlit Cloud compatibility
- ✅ No IPv6/network issues
- ✅ Automatic SSL
- ✅ Free tier available

---

# Alternative: Supabase Configuration

### Step 1: Configure Secrets in Streamlit Cloud
1. Go to your Streamlit Cloud app dashboard
2. Click on "Settings" (gear icon)
3. Go to "Secrets" tab
4. Add the following secrets:

```toml
[database]
DB_HOST = "db.imzchejztqszakqrkbpv.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "S_Sp&B&ne67HXAc"
```

### Step 2: Verify Supabase Settings
1. Log into your Supabase dashboard
2. Go to Settings > Database
3. Ensure "Enable database webhooks" is ON
4. Check that your connection pooling is configured for external connections

### Step 3: Network Configuration
Add these connection parameters to handle Streamlit Cloud networking:

```toml
[database]
DB_HOST = "db.imzchejztqszakqrkbpv.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "S_Sp&B&ne67HXAc"
DB_SSLMODE = "require"
```

### Step 4: Test Connection
After configuring secrets, restart your Streamlit app and test the pipeline execution.

## Alternative: Use Environment Variables
If secrets don't work, you can also set these as environment variables in Streamlit Cloud:
- DB_HOST
- DB_PORT  
- DB_NAME
- DB_USER
- DB_PASSWORD