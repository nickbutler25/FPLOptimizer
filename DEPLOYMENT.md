# Deployment Guide - Vercel + Railway

This guide walks you through deploying the FPL Optimizer with the frontend on Vercel and the backend on Railway.

## Prerequisites

- GitHub account
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)

## Part 1: Deploy Backend to Railway

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect the configuration from `railway.toml` and `nixpacks.toml`

### 3. Configure Environment Variables

In Railway project settings, add these environment variables:

```
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Security
SECRET_KEY=<generate-a-secure-random-key>
API_KEY=<your-api-key-for-frontend>

# CORS - Add your Vercel URL after frontend deployment
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:4200

# FPL API
FPL_API_BASE_URL=https://fantasy.premierleague.com/api
FPL_API_TIMEOUT=30
FPL_API_MAX_RETRIES=3

# Redis (Optional - Railway provides free Redis)
REDIS_HOST=<railway-redis-host>
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=300
```

To generate SECRET_KEY:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. Optional: Add Redis

1. In Railway project, click "New"
2. Select "Database" → "Add Redis"
3. Railway will automatically provide `REDIS_HOST` environment variable
4. The backend will automatically use it

### 5. Deploy

Railway will automatically deploy. Once complete:
- Note your Railway URL: `https://your-backend.up.railway.app`
- Test: `https://your-backend.up.railway.app/api/v1/health`

## Part 2: Deploy Frontend to Vercel

### 1. Update Production Environment

Edit `frontend/src/app/environments/environment.prod.ts`:

```typescript
export const environment: AppConfig = {
  production: true,
  api: {
    baseUrl: 'https://your-backend.up.railway.app/api/v1',  // Your Railway URL
    timeout: 30000,
    retryAttempts: 3
  },
  // ... rest of config
};
```

Commit the change:
```bash
git add frontend/src/app/environments/environment.prod.ts
git commit -m "Update production API URL"
git push origin main
```

### 2. Create Vercel Project

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Angular
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist/browser` (or check your angular.json)
   - **Install Command**: `npm install`

### 3. Deploy

Click "Deploy" and wait for completion.

Once deployed:
- Note your Vercel URL: `https://your-frontend.vercel.app`

### 4. Update CORS on Railway

Go back to Railway and update the `CORS_ORIGINS` environment variable:

```
CORS_ORIGINS=https://your-frontend.vercel.app
```

Railway will automatically redeploy.

## Part 3: Test the Deployment

1. Visit your Vercel URL: `https://your-frontend.vercel.app`
2. Enter your team ID and API key
3. Test fetching team data
4. Test the transfer optimizer

## Monitoring & Logs

### Railway Logs
- Go to your Railway project
- Click "Deployments" → View logs
- Check for any errors

### Vercel Logs
- Go to your Vercel project
- Click "Deployments" → View function logs
- Check browser console for frontend errors

## Environment-Specific URLs

After deployment, you'll have:

- **Production Frontend**: `https://your-frontend.vercel.app`
- **Production Backend**: `https://your-backend.up.railway.app`
- **Local Frontend**: `http://localhost:4200`
- **Local Backend**: `http://localhost:8000`

## Continuous Deployment

Both Vercel and Railway support automatic deployments:

- **Push to `main` branch** → Automatically deploys to production
- **Push to other branches** → Vercel creates preview deployments

## Cost Breakdown

### Railway Free Tier
- $5 of free credits per month
- Typically enough for a hobby project
- Includes PostgreSQL/Redis

### Vercel Free Tier
- Unlimited static deployments
- 100GB bandwidth/month
- Perfect for Angular apps

### Total Cost
**$0/month** for hobby use (within free tiers)

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` in Railway includes your Vercel URL
- Check browser console for specific error

### API Connection Errors
- Verify `environment.prod.ts` has correct Railway URL
- Test backend health endpoint directly

### Build Failures on Vercel
- Check build logs
- Ensure `frontend/package.json` has all dependencies
- Verify Angular configuration

### Build Failures on Railway
- Check deployment logs
- Verify `backend/requirements.txt` includes all dependencies (especially cvxpy, numpy, glpk)
- Railway timeout is 10 minutes for builds

## Custom Domains (Optional)

### Vercel Custom Domain
1. Go to Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### Railway Custom Domain
1. Go to Railway project settings
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Configure DNS with provided CNAME

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate API keys** - Change keys periodically in Railway settings
3. **Enable HTTPS** - Both Vercel and Railway provide free SSL
4. **Rate limiting** - Consider adding rate limiting to FastAPI
5. **Monitor logs** - Check for suspicious activity

## Updating the Application

To deploy updates:

```bash
# Make your changes
git add .
git commit -m "Your update message"
git push origin main
```

Both Vercel and Railway will automatically deploy the changes.

## Rollback

### Vercel
1. Go to "Deployments"
2. Find previous working deployment
3. Click "Promote to Production"

### Railway
1. Go to "Deployments"
2. Find previous deployment
3. Click "Redeploy"

## Next Steps

- [ ] Set up custom domains
- [ ] Add monitoring (Railway provides built-in metrics)
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Add analytics to frontend
- [ ] Configure backup strategy for any data