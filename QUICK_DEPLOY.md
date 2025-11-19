# Quick Deployment Guide - 100% FREE

## TL;DR - Get your app live in 15 minutes (completely free!)

### Step 1: Deploy Backend (Render) - 5 minutes ✅ FREE

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Render Setup**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your `FPLOptimizer` repository
   - Render auto-detects `render.yaml` ✅

3. **Configure (Auto-filled from render.yaml)**
   - **Name**: fpl-optimizer-api
   - **Runtime**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free ✅

4. **Important: Update CORS_ORIGINS**
   After deployment, in Render Dashboard:
   - Go to your service → Environment
   - Find `CORS_ORIGINS` variable
   - Update to: `http://localhost:4200` (for now)
   - Click "Save Changes"

5. **Deploy** ✅
   - Render deploys automatically (takes 3-5 minutes)
   - Copy your URL: `https://fpl-optimizer-api.onrender.com`
   - Test: Visit `https://your-url.onrender.com/api/v1/health`
   - ⚠️ First request takes 30 seconds (app is sleeping)

### Step 2: Deploy Frontend (Vercel) - 5 minutes ✅ FREE

1. **Update Production Config**

   Edit `frontend/src/app/environments/environment.prod.ts`:
   ```typescript
   baseUrl: 'https://fpl-optimizer-api.onrender.com/api/v1'  // Your Render URL
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

1. Go back to **Render** → Your Service → Environment
2. Update `CORS_ORIGINS`:
   ```
   https://fpl-optimizer.vercel.app
   ```
3. Click "Save Changes" (Render redeploys automatically) ✅

### Step 4: Test - 3 minutes

Visit your Vercel URL:
- ⚠️ **First load**: Wait 30 seconds for Render to wake up
- Enter team ID
- Enter API key (find in Render → Environment → API_KEY)
- Load team data
- Run transfer optimizer

## Done! 🎉

Your app is now live:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-api.onrender.com

**Total Cost: $0/month** 💰

## Important: Render Free Tier Behavior

⚠️ **Apps sleep after 15 minutes of inactivity**
- First request after sleeping takes ~30 seconds to wake up
- Subsequent requests are instant
- Perfect for personal use!

💡 **Tip**: Keep the app warm by visiting it regularly, or use a free uptime monitor like [UptimeRobot](https://uptimerobot.com/) to ping it every 14 minutes.

## Common Issues

### CORS Error
**Problem**: Frontend can't reach backend
**Fix**: Make sure Render `CORS_ORIGINS` includes your exact Vercel URL (with https://)

### 503 Service Unavailable
**Problem**: Backend is sleeping
**Fix**: Wait 30 seconds and refresh. This is normal on free tier!

### API Key Error
**Problem**: 401 Unauthorized
**Fix**:
1. Go to Render → Environment → find `API_KEY` value
2. Use that exact value in your frontend

### Build Failed on Render
**Problem**: Python dependencies failing
**Fix**:
- Check Render logs in Dashboard
- Ensure `backend/requirements.txt` includes all dependencies
- CVXPY might take 3-5 minutes to install (normal)

### Build Failed on Vercel
**Problem**: Angular build errors
**Fix**: Make sure `frontend/package.json` has all dependencies

## Free Tier Limits

✅ **Render Free Tier**:
- 750 hours/month (31 days x 24 hours = 744 hours)
- Enough for 1 app running 24/7
- Auto-sleeps after 15min inactivity
- 100GB bandwidth/month
- Free SSL certificate

✅ **Vercel Free Tier**:
- Unlimited deployments
- 100GB bandwidth/month
- Free SSL certificate

**Total cost: $0/month** 🎉

## Keeping Your App Awake (Optional)

If you don't want the 30-second cold start:

### Option 1: UptimeRobot (Free)
1. Sign up at https://uptimerobot.com/
2. Add new monitor:
   - Type: HTTP(s)
   - URL: `https://your-backend.onrender.com/api/v1/health`
   - Interval: 14 minutes
3. Your app stays warm 24/7! ✅

### Option 2: Cron-job.org (Free)
1. Sign up at https://cron-job.org/
2. Create new cron job:
   - URL: `https://your-backend.onrender.com/api/v1/health`
   - Interval: Every 14 minutes
3. Done! ✅

## Update Your App

```bash
# Make changes
git add .
git commit -m "Update"
git push
```

Both platforms auto-deploy on push to `main` ✅

## Getting API Key from Render

1. Go to Render Dashboard
2. Click your service
3. Click "Environment" in left sidebar
4. Find `API_KEY` variable
5. Click the eye icon to reveal value
6. Copy and use in your frontend

## Next Steps

- [ ] Set up UptimeRobot to keep app warm (optional)
- [ ] Add custom domain to Vercel (optional)
- [ ] Set up error monitoring with Sentry (optional)
- [ ] Add analytics to frontend (optional)

## Cost Comparison

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Render** | ✅ Free forever | $7/month (no sleep) |
| **Vercel** | ✅ Free forever | $20/month (team features) |
| **Railway** | ❌ No free tier | $5/month minimum |

**Recommendation**: Start with free tier, upgrade Render to $7/month only if you need instant response times.