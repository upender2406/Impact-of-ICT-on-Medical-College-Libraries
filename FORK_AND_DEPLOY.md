# 🔀 Fork and Deploy Guide

## Why You Need to Fork

Since you don't own the repository `https://github.com/Rahul-Sanskar/ict-impact-dashboard`, you need to **fork it** to your own GitHub account before deploying to Vercel.

### What is Forking?
Forking creates a **copy** of the repository under your GitHub account, giving you full control to:
- ✅ Make changes without affecting the original
- ✅ Deploy to Vercel with automatic deployments
- ✅ Push updates anytime
- ✅ Sync with the original repo if needed

---

## 📋 Complete Workflow

```
Original Repo (Rahul-Sanskar)
         ↓
    [Fork on GitHub]
         ↓
  Your Forked Repo (YOUR-USERNAME)
         ↓
  [Update Local Git Remote]
         ↓
  [Push Changes to Your Fork]
         ↓
  [Deploy to Vercel from Your Fork]
         ↓
    ✅ Deployed App
```

---

## 🚀 Step-by-Step Instructions

### **Step 1: Fork the Repository on GitHub**

1. **Open your browser** and go to:
   ```
   https://github.com/Rahul-Sanskar/ict-impact-dashboard
   ```

2. **Click the "Fork" button** in the top-right corner
   - It's next to the "Star" button
   - You might need to sign in to GitHub first

3. **Wait for the fork to complete** (takes a few seconds)
   - GitHub will create a copy at: `https://github.com/YOUR-USERNAME/ict-impact-dashboard`
   - Replace `YOUR-USERNAME` with your actual GitHub username

4. **Verify the fork:**
   - You should see "forked from Rahul-Sanskar/ict-impact-dashboard" under the repo name
   - The URL should be: `https://github.com/YOUR-USERNAME/ict-impact-dashboard`

---

### **Step 2: Update Your Local Repository**

Now you need to tell your local Git to push to **your fork** instead of the original repo.

**Open PowerShell/Terminal and run:**

```bash
# Navigate to your project
cd c:\Users\agb83\Documents\Thesisly\17 Rahul\ict-impact-dashboard

# Check current remote (should show Rahul-Sanskar's repo)
git remote -v

# Change origin to YOUR fork (replace YOUR-USERNAME with your GitHub username)
git remote set-url origin https://github.com/YOUR-USERNAME/ict-impact-dashboard.git

# Verify the change
git remote -v
# Should now show YOUR-USERNAME instead of Rahul-Sanskar
```

**Expected output:**
```
origin  https://github.com/YOUR-USERNAME/ict-impact-dashboard.git (fetch)
origin  https://github.com/YOUR-USERNAME/ict-impact-dashboard.git (push)
```

---

### **Step 3: (Optional) Keep Original Repo as Upstream**

This allows you to sync with the original repo later if needed:

```bash
# Add original repo as 'upstream'
git remote add upstream https://github.com/Rahul-Sanskar/ict-impact-dashboard.git

# Verify
git remote -v
# Should show both 'origin' (your fork) and 'upstream' (original)
```

**When to sync with upstream:**
If the original repo gets updates and you want them:
```bash
git fetch upstream
git merge upstream/main
git push origin main
```

---

### **Step 4: Push Your Changes to Your Fork**

```bash
# Stage all changes
git add .

# Commit with a message
git commit -m "Add Vercel deployment configuration"

# Push to YOUR fork
git push origin main
```

**If this is your first push to the fork, you might need to authenticate with GitHub.**

---

### **Step 5: Deploy to Vercel from Your Fork**

Now you can deploy to Vercel using **your forked repository**:

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **Click "Add New..." → "Project"**
4. **Find YOUR forked repository:**
   - Look for: `YOUR-USERNAME/ict-impact-dashboard`
   - NOT: `Rahul-Sanskar/ict-impact-dashboard`
5. **Click "Import"**
6. **Configure:**
   - Framework: **Vite**
   - Root Directory: **frontend** ← Click "Edit" and select this
   - Build Command: `npm run build`
   - Output Directory: `dist`
7. **Add Environment Variable:**
   - Name: `VITE_API_URL`
   - Value: Your backend URL (e.g., `http://localhost:8000` or production URL)
8. **Click "Deploy"**

---

## 🎯 Quick Reference Commands

### Check Current Remote
```bash
git remote -v
```

### Change to Your Fork
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/ict-impact-dashboard.git
```

### Add Original as Upstream
```bash
git remote add upstream https://github.com/Rahul-Sanskar/ict-impact-dashboard.git
```

### Push to Your Fork
```bash
git add .
git commit -m "Your message"
git push origin main
```

### Sync with Original Repo (if needed)
```bash
git fetch upstream
git merge upstream/main
git push origin main
```

---

## ✅ Verification Checklist

After forking and updating your local repo:

- [ ] Fork exists at `https://github.com/YOUR-USERNAME/ict-impact-dashboard`
- [ ] `git remote -v` shows YOUR-USERNAME in the origin URL
- [ ] Successfully pushed changes: `git push origin main`
- [ ] Can see your commits on GitHub at your fork's URL
- [ ] Ready to import YOUR fork in Vercel

---

## 🔄 Automatic Deployments

Once deployed from your fork:

- **Push to `main` branch** → Vercel auto-deploys to production
- **Push to other branches** → Vercel creates preview deployments
- **Create pull requests** → Vercel creates preview deployments

---

## ❓ Troubleshooting

### "Permission denied" when pushing
**Solution:** You haven't updated the remote URL to your fork yet.
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/ict-impact-dashboard.git
```

### "Repository not found" in Vercel
**Solution:** Make sure you're importing YOUR fork, not the original repo.

### Can't find your fork in Vercel
**Solution:** 
1. Make sure you forked the repo on GitHub
2. Refresh the Vercel import page
3. Check if you're signed in with the correct GitHub account

### Want to sync with original repo
**Solution:**
```bash
git fetch upstream
git merge upstream/main
git push origin main
```

---

## 📚 Additional Resources

- **GitHub Forking Guide:** https://docs.github.com/en/get-started/quickstart/fork-a-repo
- **Vercel Deployment Docs:** https://vercel.com/docs/deployments/overview
- **Git Remote Management:** https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes

---

## 🎉 Summary

1. **Fork** the repo on GitHub
2. **Update** your local git remote to your fork
3. **Push** your changes to your fork
4. **Deploy** from your fork on Vercel
5. **Enjoy** automatic deployments! 🚀

**Your forked repo:** `https://github.com/YOUR-USERNAME/ict-impact-dashboard`

**Your deployed app:** `https://your-project.vercel.app` (after deployment)

---

**Need help?** Check the other deployment guides:
- `.agent/workflows/deploy-vercel.md` - Detailed deployment steps
- `VERCEL_DEPLOYMENT_CHECKLIST.md` - Quick checklist
- `README.md` - Full project documentation

