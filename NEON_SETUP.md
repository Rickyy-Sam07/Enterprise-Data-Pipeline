# Neon DB Setup Instructions

## Why Neon DB?
- Better Streamlit Cloud compatibility
- Reliable IPv4 connections
- No network restriction issues
- Free tier available

## Setup Steps:

### 1. Create Neon Account
1. Go to https://neon.tech
2. Sign up with GitHub/Google
3. Create new project

### 2. Get Connection Details
After creating project, you'll get:
- Host: `ep-xxx-xxx.us-east-1.aws.neon.tech`
- Database: `neondb`
- Username: `neondb_owner`
- Password: `generated_password`

### 3. Update Streamlit Secrets
Replace Supabase config with Neon:

```toml
[database]
DB_HOST = "your-neon-host.us-east-1.aws.neon.tech"
DB_PORT = 5432
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "your_neon_password"
```

### 4. Update Local .env
```
DB_HOST=your-neon-host.us-east-1.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=your_neon_password
```

### 5. Test Connection
Neon provides better connectivity with Streamlit Cloud out of the box.

## Benefits:
- ✅ No IPv6 issues
- ✅ No network restrictions
- ✅ Better Streamlit compatibility
- ✅ Automatic SSL
- ✅ Free tier: 512MB storage