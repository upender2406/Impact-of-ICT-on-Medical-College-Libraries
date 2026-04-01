# Vercel Deployment Quick Checklist

## Pre-Deployment Checklist

- [ ] **Fork the repository** (if you don't own it)
  - Go to https://github.com/Rahul-Sanskar/ict-impact-dashboard
  - Click "Fork" button
  - Update local git remote: `git remote set-url origin https://github.com/YOUR-USERNAME/ict-impact-dashboard.git`
- [ ] All code changes committed to git
- [ ] Latest code pushed to **your forked repository** on GitHub
- [ ] Backend URL ready (if deployed)
- [ ] Vercel account created

## Deployment Steps

- [ ] **Step 1:** Log in to [vercel.com](https://vercel.com) with GitHub
- [ ] **Step 2:** Click "Add New..." → "Project"
- [ ] **Step 3:** Import `ict-impact-dashboard` repository
- [ ] **Step 4:** Configure settings:
  - Framework: **Vite**
  - Root Directory: **frontend**
  - Build Command: `npm run build`
  - Output Directory: `dist`
- [ ] **Step 5:** Add environment variable:
  - Name: `VITE_API_URL`
  - Value: Your backend URL (e.g., `https://your-backend.onrender.com`)
- [ ] **Step 6:** Click "Deploy"
- [ ] **Step 7:** Wait for build to complete (1-2 minutes)

## Post-Deployment Checklist

- [ ] Visit deployed URL and verify homepage loads
- [ ] Check browser console for errors (F12)
- [ ] Update backend `CORS_ORIGINS` with Vercel URL
- [ ] Test login/signup functionality
- [ ] Test API calls (check Network tab)
- [ ] Verify data submission works

## Your Deployment Info

**Frontend URL:** `https://_________________________.vercel.app`

**Backend URL:** `https://_________________________.onrender.com`

**Deployment Date:** _______________

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Build fails | Check build logs in Vercel dashboard |
| CORS errors | Update `CORS_ORIGINS` on backend |
| API calls fail | Verify `VITE_API_URL` is correct |
| Blank page | Check browser console for errors |
| 404 on refresh | Already configured in `vercel.json` |

## Environment Variables

### Frontend (Vercel)
```
VITE_API_URL=https://your-backend-url.onrender.com
```

### Backend (Render)
```
CORS_ORIGINS=https://your-frontend.vercel.app,https://www.your-frontend.vercel.app
DATABASE_URL=your-postgresql-connection-string
SECRET_KEY=your-secret-key
PORT=8000
ENVIRONMENT=production
```

## Automatic Deployments

✅ Push to `main` branch → Auto-deploys to production
✅ Push to other branches → Creates preview deployment
✅ Pull requests → Creates preview with unique URL

## Useful Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Project Settings:** https://vercel.com/[your-username]/[project-name]/settings
- **Deployment Logs:** https://vercel.com/[your-username]/[project-name]/deployments
- **Documentation:** https://vercel.com/docs

---

**Last Updated:** 2026-01-23
