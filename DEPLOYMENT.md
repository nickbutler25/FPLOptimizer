# Deployment Guide - Vercel + Render (100% FREE)

This guide walks you through deploying the FPL Optimizer with the frontend on Vercel and the backend on Render - both completely free!

## Prerequisites

- GitHub account
- Render account (https://render.com) - FREE, no credit card required
- Vercel account (https://vercel.com) - FREE

## Quick Start

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a condensed 15-minute deployment guide.

## Part 1: Deploy Backend to Render

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Create Render Web Service

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub and select your `FPLOptimizer` repository
4. Render auto-detects `render.yaml` configuration

### 3. Service Configuration

Auto-filled from `render.yaml`:
- **Name**: `fpl-optimizer-api`
- **Runtime**: Python 3
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Free ✅

### 4. Environment Variables

Auto-configured, but verify:
- `ENVIRONMENT=production`
- `API_KEY` (auto-generated - note this!)
- `CORS_ORIGINS=http://localhost:4200` (update after frontend deployment)

### 5. Deploy & Test

- Deploy takes 3-5 minutes
- URL: `https://fpl-optimizer-api.onrender.com`
- Test: `https://your-url.onrender.com/api/v1/health`
- First request takes 30s (waking from sleep)

## Part 2: Deploy Frontend to Vercel

### 1. Update Production Config

Edit `frontend/src/app/environments/environment.prod.ts` with your Render URL, commit and push.

### 2. Create Vercel Project

1. Go to https://vercel.com/new
2. Import GitHub repository
3. Set Root Directory: `frontend`
4. Deploy (auto-detects Angular)

### 3. Update CORS

Update `CORS_ORIGINS` in Render to your Vercel URL.

## Free Tier Details

**Render**: 750 hours/month, sleeps after 15min inactivity
**Vercel**: Unlimited deployments, 100GB bandwidth/month
**Total Cost**: $0/month 🎉

## Keeping App Awake (Optional)

Use UptimeRobot (free) to ping your backend every 14 minutes:
- Sign up at https://uptimerobot.com/
- Monitor: `https://your-backend.onrender.com/api/v1/health`
- Interval: 14 minutes

## Troubleshooting

### CORS Errors
Ensure `CORS_ORIGINS` in Render includes exact Vercel URL with `https://`

### 503 Errors
App is sleeping - wait 30 seconds and refresh

### Build Failures
- Render: Check logs, CVXPY takes 3-5 minutes to install
- Vercel: Verify all dependencies in package.json

## Continuous Deployment

Push to `main` → auto-deploys to both platforms ✅

## Cost Comparison

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| Render | ✅ Free | $7/month (no sleep) |
| Vercel | ✅ Free | $20/month (team) |
| Railway | ❌ None | $5/month minimum |

For full documentation, see [QUICK_DEPLOY.md](QUICK_DEPLOY.md).