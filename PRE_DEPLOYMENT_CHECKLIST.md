# Pre-Deployment Checklist

## 📋 Before Deploying to Render & Vercel

### Backend (Render) - Database Setup
- [ ] Created PostgreSQL database on Render or Neon
- [ ] Copied full connection string (e.g., `postgresql://user:pass@host:5432/db`)
- [ ] Verified connection string contains **ACTUAL** hostname (not "host")
- [ ] Verified connection string contains **ACTUAL** port number (not "port")
- [ ] Verified connection string contains **ACTUAL** database name
- [ ] Generated SECRET_KEY with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Tested DATABASE_URL locally before deploying

### Backend (Render) - Environment Variables
- [ ] Set `DATABASE_URL` to full PostgreSQL connection string
- [ ] Set `SECRET_KEY` to generated random string
- [ ] Set `PORT=8000`
- [ ] Set `HOST=0.0.0.0`
- [ ] Set `ENVIRONMENT=production`
- [ ] Verified all environment variables are filled (no empty values)
- [ ] NO SECRETS left in code or version control

### Frontend (Vercel) - Deployment Ready
- [ ] Frontend builds locally without errors: `npm run build`
- [ ] `dist/` folder is created successfully
- [ ] vercel.json is configured correctly
- [ ] No `.env.local` or secrets in git
- [ ] `.env.example` provided (without secrets)

### Frontend (Vercel) - Environment Variables
- [ ] Deployed frontend to Vercel first
- [ ] Noted the Vercel domain (e.g., `https://ict-dashboard.vercel.app`)
- [ ] Did NOT set `VITE_API_URL` yet (wait for backend)

### Backend (Render) - After Frontend Deployment
- [ ] Backend deployed to Render first
- [ ] Noted the Render backend domain (e.g., `https://ict-backend.render.com`)
- [ ] Set `CORS_ORIGINS` in Render environment to Vercel domain(s):
  ```
  https://ict-dashboard.vercel.app,https://www.ict-dashboard.vercel.app
  ```
- [ ] Redeployed backend to apply CORS changes

### Frontend (Vercel) - After Backend Deployment
- [ ] Set `VITE_API_URL` environment variable to Render domain:
  ```
  https://ict-backend.render.com
  ```
- [ ] Redeployed frontend to apply API URL changes

### Post-Deployment Verification
- [ ] Backend health check passes: `curl https://ict-backend.render.com/health`
- [ ] Frontend loads at Vercel domain
- [ ] No CORS errors in browser console
- [ ] Can create account / login without errors
- [ ] Can submit data and see it in analytics
- [ ] API calls show correct Authorization headers
- [ ] Database connection is stable
- [ ] No "invalid literal for int" errors in logs

## 🚨 Common Mistakes to Avoid

| Mistake | Effect | Fix |
|---------|--------|-----|
| DATABASE_URL with literal `"port"` | `ValueError: invalid literal for int()` | Copy actual connection string |
| CORS_ORIGINS includes `localhost` | `CORS error in production` | Only include Vercel domain |
| VITE_API_URL is `http://` not `https://` | `Mixed content error` | Use `https://` |
| Empty environment variables | `Startup fails silently` | Fill all required variables |
| SECRET_KEY is weak placeholder | `Security vulnerability` | Generate random string |
| DATABASE_URL is wrong format | `Connection fails` | Verify format matches examples |

## 📞 If Deployment Fails

1. **Check Render logs** for specific error
2. **Review DEPLOYMENT_ERRORS.md** for that error type
3. **Verify environment variables** match checklist above
4. **Test locally** with same configuration
5. **Contact support** if issue persists

## ✅ Successful Deployment Signs

- [ ] No errors in Render build logs
- [ ] No errors in Vercel build logs
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] Frontend loads in browser
- [ ] Can authenticate and submit data
- [ ] No CORS, HTTPS, or database errors

---

**Remember:** The most common error is using placeholder text in DATABASE_URL. Always copy the FULL connection string from your database provider!
