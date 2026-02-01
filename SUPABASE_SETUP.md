# Supabase Setup Instructions

## 🚀 Quick Supabase Setup

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login and create a new project
3. Choose a region close to you
4. Wait for project to be ready (~2 minutes)

### 2. Get Database Credentials
1. In your Supabase dashboard, go to **Settings** → **Database**
2. Copy the connection details:
   - **Host**: `your-project-ref.supabase.co`
   - **Database name**: `postgres`
   - **Username**: `postgres`
   - **Password**: Your project password

### 3. Update .env File
Replace the values in `.env` with your Supabase credentials:

```env
# Supabase Configuration
DB_HOST=your-project-ref.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
```

### 4. Test Connection
Run the setup script to test your connection:
```bash
setup.bat
```

## 🔒 Security Notes
- Keep your `.env` file secure and never commit it to version control
- Use Supabase's Row Level Security (RLS) for production deployments
- Consider using environment variables in production instead of .env files

## 📊 Supabase Dashboard
After running the pipeline, you can view your data directly in Supabase:
1. Go to **Table Editor** in your Supabase dashboard
2. You'll see all the pipeline tables: `raw_sales`, `clean_sales`, `validation_results`, etc.
3. Use the **SQL Editor** to run custom queries on your data

## 🌐 Connection String Format
If you need the full connection string:
```
postgresql://postgres:your_password@your-project-ref.supabase.co:5432/postgres
```