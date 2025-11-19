# FPL Optimizer - Complete Setup Guide

This guide will help you set up and run both the backend FastAPI server and the Angular frontend.

## Project Structure

```
FPLOptimizer/
├── backend/          # FastAPI REST API
│   ├── app/         # Application code
│   ├── .env         # Environment configuration
│   └── start.py     # Quick start script
├── frontend/        # Angular application
│   └── src/app/     # Frontend code
└── SETUP.md        # This file
```

## Prerequisites

- **Backend**: Python 3.11+
- **Frontend**: Node.js 18+ and npm
- **Optional**: Redis (for caching)

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

The `.env` file is already configured with development defaults:
- API will run on `http://localhost:8000`
- API Key: `dev-api-key-change-in-production`
- Debug mode enabled
- Redis optional (will work without it)

To change settings, edit `backend/.env`

### 4. Start the Backend Server

**Option 1: Using the quick start script**
```bash
python start.py
```

**Option 2: Direct uvicorn**
```bash
python -m app.main
```

**Option 3: Using Docker**
```bash
docker-compose up --build
```

The backend will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Environment Configuration

The environment is already configured to point to the backend:
- Backend API: `http://localhost:8000/api/v1`
- Mock data: Disabled (uses real backend)

Configuration file: `frontend/src/app/environments/environment.ts`

### 4. Start the Frontend Server

```bash
npm start
```

The frontend will be available at: http://localhost:4200

## Using the Application

### 1. Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
python start.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 2. Access the Application

Open your browser to: http://localhost:4200

### 3. View an FPL Team

1. Scroll down to the "FPL Team Viewer" section
2. Enter a team ID (e.g., `123456`)
3. Check "Include current team picks" to see the squad
4. Click "Load Team"

**Finding a Team ID:**
- Go to https://fantasy.premierleague.com
- View any team
- The URL will show: `https://fantasy.premierleague.com/entry/123456/event/1`
- `123456` is the team ID

## API Endpoints

### Teams
- `GET /api/v1/teams/{team_id}` - Get team data
  - Query param: `include_picks=true/false`
- `GET /api/v1/teams/{team_id}/summary` - Get team summary

### Players
- `GET /api/v1/players` - Get all players
  - Optional filters: `position`, `team_id`, `min_cost`, `max_cost`
- `GET /api/v1/players/{player_id}` - Get specific player
- `GET /api/v1/players/top/points` - Get top players by points

### Health
- `GET /api/v1/health` - Health check (no auth required)

### Authentication

All endpoints (except `/health`) require an API key header:

```bash
curl -H "X-API-Key: dev-api-key-change-in-production" \
  http://localhost:8000/api/v1/teams/123456
```

## Testing the API

### Using curl

**Get a team:**
```bash
curl -H "X-API-Key: dev-api-key-change-in-production" \
  "http://localhost:8000/api/v1/teams/123456?include_picks=true"
```

**Get all players:**
```bash
curl -H "X-API-Key: dev-api-key-change-in-production" \
  "http://localhost:8000/api/v1/players"
```

**Get top players:**
```bash
curl -H "X-API-Key: dev-api-key-change-in-production" \
  "http://localhost:8000/api/v1/players/top/points?limit=10"
```

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter API key: `dev-api-key-change-in-production`
4. Try out any endpoint

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in backend/.env
PORT=8001
```

**Redis connection failed:**
- The app will work without Redis
- To disable the warning, set a non-existent Redis host in `.env`

**CORS errors:**
- Check `CORS_ORIGINS` in `backend/.env`
- Add your frontend URL if different from localhost:3000 or localhost:8000

### Frontend Issues

**Backend connection failed:**
- Verify backend is running on http://localhost:8000
- Check `frontend/src/app/environments/environment.ts`
- Verify API key matches backend `.env`

**API key errors:**
- Ensure API key in `frontend/src/app/services/implementations/team.service.ts`
  matches `API_KEY` in `backend/.env`

**Angular version issues:**
- Clear Angular cache:
  ```bash
  rm -rf frontend/.angular
  ```

## Development

### Backend Development

The backend uses hot-reload in development mode:
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend Development

Angular automatically reloads on file changes when using `npm start`

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## Production Deployment

### Backend

1. Update `backend/.env`:
   - Set `ENVIRONMENT=production`
   - Change `SECRET_KEY` (use `openssl rand -hex 32`)
   - Change `API_KEY` to a secure value
   - Set `DEBUG=false`

2. Use production server:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend

1. Build for production:
   ```bash
   cd frontend
   npm run build:prod
   ```

2. Update environment:
   - Set production API URL in `environment.prod.ts`
   - Update API key to match production backend

3. Serve with nginx or similar web server

## Key Features

### Backend
- ✅ RESTful API design
- ✅ Dependency injection (dependency-injector)
- ✅ Structured logging (JSON in production)
- ✅ API key authentication
- ✅ Redis caching (optional)
- ✅ Retry logic for FPL API calls
- ✅ Comprehensive error handling
- ✅ Auto-generated API documentation
- ✅ Docker support

### Frontend
- ✅ Angular 20 with standalone components
- ✅ TypeScript with full type safety
- ✅ Reactive forms with RxJS
- ✅ Error handling and loading states
- ✅ Responsive design
- ✅ Real-time API integration

## Need Help?

- Backend API Docs: http://localhost:8000/docs
- Backend logs: Check console output
- Frontend logs: Check browser console (F12)
- Issues: Check GitHub issues or create a new one

## License

MIT