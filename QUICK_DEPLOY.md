# Quick Deployment Guide

## TL;DR - Get your app live in 15 minutes

### Step 1: Deploy Backend (Railway) - 5 minutes

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Railway Setup**
   - Go to https://railway.app/new
   - Click "Deploy from GitHub repo"
   - Select your `FPLOptimizer` repository
   - Railway auto-detects Python project ✅

3. **Add Environment Variables** (Railway Dashboard → Variables)
   ```
   ENVIRONMENT=production
   DEBUG=False
   API_KEY=your-secret-api-key-here
   SECRET_KEY=generate-with-secrets.token_urlsafe-32
   CORS_ORIGINS=http://localhost:4200
   ```

4. **Deploy** ✅
   - Railway deploys automatically
   - Copy your URL: `https://fploptimizer-production-xxxx.up.railway.app`
   - Test: Visit `https://your-url.up.railway.app/api/v1/health`

### Step 2: Deploy Frontend (Vercel) - 5 minutes

1. **Update Production Config**

   Edit `frontend/src/app/environments/environment.prod.ts`:
   ```typescript
   baseUrl: 'https://your-railway-url.up.railway.app/api/v1'
   ```

   Commit:
   ```bash
   git add frontend/src/app/environments/environment.prod.ts
   git commit -m "Set production API URL"
   git push
   ```

2. **Vercel Setup**
   - Go to https://vercel.com/new
   - Import your GitHub repo
   - Set **Root Directory**: `frontend`
   - Click **Deploy** ✅

3. **Copy Vercel URL**
   - Example: `https://fpl-optimizer.vercel.app`

### Step 3: Update CORS - 2 minutes

1. Go back to **Railway** → Your Project → Variables
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-vercel-url.vercel.app
   ```
3. Railway redeploys automatically ✅

### Step 4: Test - 3 minutes

Visit your Vercel URL:
- Enter team ID
- Enter API key (the one you set in Railway)
- Load team data
- Run transfer optimizer

## Done! 🎉

Your app is now live:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-backend.up.railway.app

## Common Issues

### CORS Error
**Problem**: Frontend can't reach backend
**Fix**: Make sure Railway `CORS_ORIGINS` includes your exact Vercel URL

### API Key Error
**Problem**: 401 Unauthorized
**Fix**: Check that API_KEY in Railway matches what you're using in frontend

### Build Failed on Railway
**Problem**: Python dependencies failing
**Fix**: Check Railway logs - usually a missing package in requirements.txt

### Build Failed on Vercel
**Problem**: Angular build errors
**Fix**: Make sure `frontend/package.json` has all dependencies

## Free Tier Limits

✅ **Railway**: $5/month credit (enough for hobby projects)
✅ **Vercel**: Unlimited deployments, 100GB bandwidth

Total cost: **$0/month** for typical usage

## Update Your App

```bash
# Make changes
git add .
git commit -m "Update"
git push
```

Both platforms auto-deploy on push to `main` ✅