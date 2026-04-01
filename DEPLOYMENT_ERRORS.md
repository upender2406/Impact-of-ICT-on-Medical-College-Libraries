# Deployment Troubleshooting Guide

## Error: `ValueError: invalid literal for int() with base 10: 'port'`

### Root Cause
This error occurs when the `DATABASE_URL` environment variable contains a literal placeholder like `"port"` instead of an actual port number. SQLAlchemy tries to parse the connection string and fails because `"port"` cannot be converted to an integer.

### Example of WRONG Configuration
```
# ❌ INCORRECT - Using literal placeholders
DATABASE_URL=postgresql://user:password@host:port/database
```

### Example of CORRECT Configuration

#### For Render PostgreSQL:
```env
# ✅ CORRECT - From Render's postgres dashboard
DATABASE_URL=postgresql://user:password@dpg-abc123def456.render.postgresql.com:5432/ict_dashboard_prod
```

#### For Neon PostgreSQL:
```env
# ✅ CORRECT - From Neon's connection string
DATABASE_URL=postgresql://neondb_owner:password@ep-western-prod-123.us-east-1.neon.tech:5432/neondb
```

#### For Local Development (SQLite):
```env
# ✅ CORRECT - For development only
DATABASE_URL=sqlite:///./database/ict_survey.db
```

---

## Step-by-Step Render Deployment Fix

### 1. Create PostgreSQL Database on Render
1. Go to [render.com](https://render.com)
2. Dashboard → New → PostgreSQL
3. Fill in:
   - **Name**: `ict-dashboard-db`
   - **Database**: `ict_dashboard_prod`
   - **User**: (auto-generated)
   - **Region**: Choose closest to users
   - **PostgreSQL Version**: 15
4. Click "Create Database"

### 2. Copy the Correct Connection String
- From Render dashboard, go to your PostgreSQL instance
- Copy the **connection string** (not the URL)
- It should look like:
  ```
  postgresql://user:password@host:5432/database
  ```
  NOT like:
  ```
  postgresql://user:password@host:port/database
  ```

### 3. Update Environment Variables in Render Backend Service
1. Go to your backend web service in Render
2. Settings → Environment
3. Find/Create `DATABASE_URL` and set it to the **full connection string** copied above
4. Ensure these are also set:
   ```
   PORT=8000
   HOST=0.0.0.0
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   SECRET_KEY=<generate strong random string>
   ENVIRONMENT=production
   ```

### 4. Redeploy
1. Render dashboard → Backend service
2. Click "Clear Cache & Redeploy" or commit a change to trigger redeploy

### 5. Verify Deployment
```bash
curl https://your-backend-service.render.com/health
# Response: {"status":"healthy"}
```

---

## Critical Rules for Production Environment Variables

### ✅ DO
- ✅ Use **actual hostnames** (e.g., `dpg-abc123.render.postgresql.com`)
- ✅ Use **actual port numbers** (e.g., `5432`)
- ✅ Use **actual database names** (e.g., `ict_dashboard_prod`)
- ✅ Copy the **entire connection string** from your provider
- ✅ Generate a **strong SECRET_KEY** using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- ✅ Test the connection string locally before deploying

### ❌ DON'T
- ❌ Use placeholder text like `"host"`, `"port"`, `"password"`
- ❌ Copy incomplete URLs without actual values
- ❌ Leave environment variables empty in production
- ❌ Use localhost domains (e.g., `localhost:5432`)
- ❌ Use weak or placeholder secrets like `"your-secret-key-here"`

---

## Complete Correct Environment Variables for Render

### Minimal Setup (Render PostgreSQL)
```env
# From Render PostgreSQL dashboard - copy the connection string
DATABASE_URL=postgresql://user:password@dpg-xxxx.render.postgresql.com:5432/ict_dashboard_prod

# Generated with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=generate_a_strong_random_string_here

# Your Vercel frontend domain (after it's deployed)
CORS_ORIGINS=https://ict-dashboard.vercel.app,https://www.ict-dashboard.vercel.app

# Standard settings
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production
```

### Alternative Setup (Neon PostgreSQL)
```env
# From Neon's connection string
DATABASE_URL=postgresql://neondb_owner:password@ep-western-prod-123.us-east-1.neon.tech:5432/neondb

SECRET_KEY=generate_a_strong_random_string_here
CORS_ORIGINS=https://ict-dashboard.vercel.app
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production
```

---

## Debugging Steps

### 1. Check if DATABASE_URL is set correctly
```bash
# In Render service logs, you should NOT see "invalid literal for int"
# If you see it, the DATABASE_URL is wrong
```

### 2. Test DATABASE_URL locally
```bash
# On your machine, set the DATABASE_URL and try:
python -c "from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); print('✓ Connection string is valid')"
```

### 3. View Render Logs in Real-Time
- Render dashboard → Backend service → Logs
- Watch logs as you trigger a redeploy
- Look for the exact error message

### 4. Common DATABASE_URL Format Errors
```
❌ postgresql://user:password@host:port/db      # "port" is literal!
❌ postgresql://user:password@host:5432/db      # Missing hostname!
❌ postgresql://user@password@host:5432/db      # Wrong @ placement!
✅ postgresql://user:password@hostname:5432/db  # Correct format
```

---

## Prevention Checklist

Before redeploying to Render:
- [ ] DATABASE_URL contains actual hostname (not "host")
- [ ] DATABASE_URL contains actual port number (not "port")
- [ ] DATABASE_URL contains actual database name (not "database")
- [ ] CONNECTION STRING is copied from your database provider
- [ ] SECRET_KEY is a generated random string (not a placeholder)
- [ ] CORS_ORIGINS matches your Vercel frontend domain
- [ ] All environment variables are filled (no empty values)
- [ ] Tested DATABASE_URL format locally
- [ ] PORT is set to 8000
- [ ] HOST is set to 0.0.0.0
- [ ] ENVIRONMENT is set to production

---

## Quick Reference: Database Connection String Locations

### Render PostgreSQL
1. Render Dashboard → PostgreSQL instance
2. Look for "External Database URL" or "Internal Database URL"
3. Copy the entire string (will look like `postgresql://user:pass@dpg-xxx.render.postgresql.com:5432/db`)

### Neon PostgreSQL
1. Neon Dashboard → Project → Connection string
2. Copy the "Connection string" (will look like `postgresql://user:pass@ep-xxx.neon.tech:5432/db`)

### Heroku PostgreSQL
1. Heroku Dashboard → Resources → Heroku Postgres
2. Click on the database
3. Settings → Database Credentials
4. Copy the "URI" field

---

## Still Stuck?

If the error persists:
1. Check Render logs for exact error message
2. Verify DATABASE_URL format matches examples above
3. Test DATABASE_URL locally before deploying
4. Ensure port number is 5432 (standard PostgreSQL port)
5. Verify username and password are correct
6. Check that database name is spelled correctly
