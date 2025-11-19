# FPL Optimizer

> A web application that helps Fantasy Premier League users find the optimal team composition within budget constraints using mathematical optimization techniques.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-20.1-red.svg)](https://angular.io/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)

## Live Application

- **Frontend**: [https://fpl-optimizer-eight.vercel.app](https://fpl-optimizer-eight.vercel.app)
- **Backend API**: [https://fpl-optimizer-api.onrender.com](https://fpl-optimizer-api.onrender.com)
- **API Documentation**: [https://fpl-optimizer-api.onrender.com/docs](https://fpl-optimizer-api.onrender.com/docs)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd FPLOptimizer

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# In a new terminal - Frontend setup
cd frontend
npm install
ng serve
```

Visit `http://localhost:4200` to see the application!

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup](#docker-setup)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**FPL Optimizer** analyzes real-time player data from the official Fantasy Premier League API and recommends the best-value team that maximizes points per cost while respecting all FPL constraints:

- ✅ 11 players total
- ✅ Maximum 3 players per team
- ✅ Valid formations (e.g., 3-5-2, 4-4-2, 4-3-3)
- ✅ Budget constraints (£3.0M - £15.0M)
- ✅ Player availability and injury status

### Use Case

Users input their budget and preferred formation, and the optimizer provides actionable team recommendations based on:
- Current form and points
- Cost efficiency (points per £)
- Minutes played
- Ownership percentage
- Team distribution

---

## Features

### Current Features

- ✅ **Real-time FPL Data** - Live player statistics from official FPL API
- ✅ **Advanced Filtering** - Filter by position, team, cost, form, minutes, ownership
- ✅ **Team Management** - View and analyze FPL teams by entry ID
- ✅ **Transfer Optimization** - Multi-week transfer planning using CVXPY optimization
- ✅ **Fixture Analysis** - Expected points calculation based on upcoming fixture difficulty
- ✅ **Smart Caching** - Redis-based caching with automatic invalidation
- ✅ **Health Monitoring** - Comprehensive health checks for production deployments
- ✅ **Responsive UI** - Modern Tailwind CSS design with Premier League branding
- ✅ **Multi-Environment** - Dev/Staging/Production configurations with environment-specific builds
- ✅ **Production Deployment** - Backend on Render, Frontend on Vercel
- ✅ **Public API Access** - No authentication required for public endpoints

### Coming Soon

- 🚧 **Formation Builder** - Interactive formation selector with visual team builder
- 🚧 **Statistical Analysis Dashboard** - Player trends, form analysis, and predictive analytics
- 🚧 **Squad Comparison** - Compare multiple FPL teams side-by-side
- 🚧 **Points Prediction** - Machine learning-based points forecasting

---

## Architecture

The project implements **Clean Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Angular 20)                   │
│                  Tailwind CSS + TypeScript                   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────────┐
│                  API Layer (FastAPI)                         │
│              OpenAPI/Swagger Documentation                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Business Logic Layer (Services)                 │
│      Data Mapping, Filtering, Validation, Caching           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│           Repository Layer (Data Access)                     │
│         HTTP Client + Retry Logic + Cache Management         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                Domain Layer (Entities)                       │
│         Player, Position, InjuryStatus, Enums                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              External Data Source                            │
│      Official FPL API (fantasy.premierleague.com)            │
└──────────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

- **Clean Architecture** - Separated layers with clear dependencies
- **Repository Pattern** - Abstract data access behind interfaces
- **Dependency Injection** - Loose coupling via container-based DI
- **DTOs** - Request/Response objects separate from domain entities
- **Service Factory** - Support for real vs. mock implementations
- **Cache-aside** - Check cache first, fallback to API, update cache
- **Async/Await** - Fully asynchronous for high-performance concurrent requests

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI | Modern async REST API framework |
| Server | Uvicorn | ASGI server for async Python |
| Validation | Pydantic v2 | Data validation and settings management |
| HTTP Client | httpx | Async HTTP requests to FPL API |
| Optimization | CVXPY | Convex optimization for transfer planning |
| Caching | Redis / aiocache | Distributed caching with TTL |
| Logging | python-json-logger | Structured JSON logging |
| Configuration | python-dotenv | Environment variable management |
| Type Safety | typing-extensions | Python type hints |
| Security | python-jose, passlib | JWT tokens and password hashing |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Angular 20 | Latest Angular with standalone components |
| Language | TypeScript 5.8 | Type-safe JavaScript superset |
| Styling | Tailwind CSS 3.4 | Utility-first CSS framework |
| HTTP | Angular HttpClient | Built-in HTTP client with RxJS |
| Reactive | RxJS 7.8 | Observable-based reactive programming |
| Testing | Jasmine + Karma | Unit and integration testing |
| Build | Angular CLI | Development and production builds |

### Infrastructure & Deployment

| Component | Technology |
|-----------|-----------|
| Backend Hosting | Render (Free Tier) |
| Frontend Hosting | Vercel |
| Caching | Redis (Render) |
| Containerization | Docker + Docker Compose |
| Version Control | Git + GitHub |
| CI/CD | Automatic deployment on push to main |
| API Documentation | OpenAPI 3.0 (Swagger/ReDoc) |

---

## Prerequisites

Ensure you have the following installed:

### Backend Requirements
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **virtualenv** (optional but recommended)

### Frontend Requirements
- **Node.js 18+** ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)
- **Angular CLI** (install globally): `npm install -g @angular/cli`

### Optional
- **Docker** ([Download](https://www.docker.com/get-started))
- **Docker Compose** (included with Docker Desktop)
- **Git** ([Download](https://git-scm.com/))

---

## Getting Started

### Clone the Repository

```bash
git clone <repository-url>
cd FPLOptimizer
```

---

### Backend Setup

#### 1. Navigate to Backend Directory

```bash
cd backend
```

#### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (includes testing tools):
```bash
pip install -r requirements-dev.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Copy from example
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Application Settings
APP_NAME=FPL Optimizer API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# FPL API Configuration
FPL_API_BASE_URL=https://fantasy.premierleague.com/api
FPL_API_TIMEOUT=30
FPL_API_MAX_RETRIES=3

# Cache Configuration (Redis)
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

#### 5. Start the Backend Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the Makefile (if available)
make run
```

The API will be available at:
- **API Base:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

#### 6. Verify Backend is Running

Open your browser and navigate to:
```
http://localhost:8000/api/v1/health
```

You should see a response indicating the health status of the API and its dependencies (FPL API, Redis cache, etc.).

---

### Frontend Setup

#### 1. Navigate to Frontend Directory

Open a **new terminal** and navigate to frontend:

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment (Optional)

Edit environment files in `src/environments/`:

**`environment.ts` (Development):**
```typescript
import { AppConfig } from "../app/config/app.config";

export const environment: AppConfig = {
  production: false,
  api: {
    baseUrl: 'http://localhost:8000/api/v1',
    timeout: 30000,
    retryAttempts: 3
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: false,
    enableMockData: false
  },
  logging: {
    level: 'debug' as const,
    enableConsoleLogging: true
  }
};
```

**`environment.prod.ts` (Production):**
```typescript
import { AppConfig } from "../app/config/app.config";

export const environment: AppConfig = {
  production: true,
  api: {
    baseUrl: 'https://fpl-optimizer-api.onrender.com/api/v1',
    timeout: 30000,
    retryAttempts: 3
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: false,
    enableMockData: false
  },
  logging: {
    level: 'error' as const,
    enableConsoleLogging: false
  }
};
```

#### 4. Start the Development Server

```bash
ng serve
```

Or specify a port:
```bash
ng serve --port 4200
```

The application will be available at:
```
http://localhost:4200
```

#### 5. Verify Frontend is Running

Open your browser and navigate to `http://localhost:4200`. You should see the FPL Optimizer UI with the Premier League branding.

---

### Docker Setup

#### 1. Using Docker Compose (Easiest)

Start both backend and frontend together:

```bash
# From the project root
docker-compose up
```

With rebuild:
```bash
docker-compose up --build
```

In detached mode:
```bash
docker-compose up -d
```

Stop services:
```bash
docker-compose down
```

#### 2. Build Individual Containers

**Backend:**
```bash
cd backend
docker build -t fpl-optimizer-backend .
docker run -p 8000:8000 fpl-optimizer-backend
```

**Frontend:**
```bash
cd frontend
docker build -t fpl-optimizer-frontend .
docker run -p 4200:80 fpl-optimizer-frontend
```

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints Overview

#### Root Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root with information and available endpoints |
| `GET` | `/api/v1/health` | Comprehensive health check (all systems) |

#### Players API (`/api/v1/players`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/players` | Get filtered list of players |
| `GET` | `/api/v1/players/{id}` | Get specific player by ID |
| `GET` | `/api/v1/players/top/points` | Get top performing players by total points |
| `GET` | `/api/v1/players/fixtures/upcoming` | Get all players with expected points for next 5 gameweeks |

#### Teams API (`/api/v1/teams`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/teams/{team_id}` | Get FPL team data by entry ID |
| `GET` | `/api/v1/teams/{team_id}/summary` | Get team summary with key statistics |
| `POST` | `/api/v1/teams/{team_id}/transfer-plan` | Generate optimal transfer plan for N gameweeks |

**Query Parameters for `/api/v1/players`:**

```
positions         : string[]  - Filter by position (GKP, DEF, MID, FWD)
teams             : string[]  - Filter by team name
min_cost          : float     - Minimum player cost (£M)
max_cost          : float     - Maximum player cost (£M)
min_points        : int       - Minimum total points
max_points        : int       - Maximum total points
min_form          : float     - Minimum form rating
available_only    : bool      - Only available players (not injured)
min_minutes       : int       - Minimum minutes played
min_selected_percent : float  - Minimum ownership percentage
max_selected_percent : float  - Maximum ownership percentage
search_term       : string    - Search player names
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/players?positions=FWD&min_cost=5.0&max_cost=10.0&available_only=true"
```

**Example Response:**

```json
{
  "status": "success",
  "players": [
    {
      "id": 123,
      "name": "Example Player",
      "web_name": "Player",
      "team": "Arsenal",
      "position": "FWD",
      "cost": 8.5,
      "total_points": 150,
      "points_per_game": 5.2,
      "form": 7.8,
      "minutes": 1350,
      "goals_scored": 12,
      "assists": 5,
      "clean_sheets": 0,
      "selected_by_percent": 45.3,
      "injury_status": "Available"
    }
  ],
  "total_count": 1,
  "filters_applied": {
    "positions": ["FWD"],
    "min_cost": 5.0,
    "max_cost": 10.0,
    "available_only": true
  },
  "data_source": "FPL_API",
  "cache_hit": false
}
```

#### Health Check API (`/api/v1/health`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health/` | Comprehensive health check (all systems) |
| `GET` | `/api/v1/health/simple` | Simple health check (app only) |
| `GET` | `/api/v1/health/status` | Detailed status information |
| `GET` | `/api/v1/health/ready` | Kubernetes readiness probe |
| `GET` | `/api/v1/health/live` | Kubernetes liveness probe |
| `GET` | `/api/v1/health/metrics` | Prometheus-compatible metrics |

---

## Project Structure

```
FPLOptimizer/
├── backend/                          # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py                   # Application entry point
│   │   ├── api/                      # REST API Layer
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── players.py    # Players endpoints
│   │   │   │   │   └── health.py     # Health check endpoints
│   │   │   │   └── router.py         # API v1 router
│   │   │   ├── dependencies.py       # Shared dependencies
│   │   │   ├── exceptions.py         # API exception handlers
│   │   │   └── middleware.py         # API middleware
│   │   ├── core/                     # Application Core
│   │   │   ├── config.py             # Configuration management
│   │   │   ├── container.py          # Dependency injection container
│   │   │   ├── exceptions.py         # Custom exceptions
│   │   │   ├── logging.py            # Logging configuration
│   │   │   ├── middleware.py         # Core middleware
│   │   │   └── security.py           # Security utilities
│   │   ├── domain/                   # Domain Layer
│   │   │   ├── entities/             # Domain entities
│   │   │   │   └── player.py         # Player entity
│   │   │   ├── enums/                # Enumerations
│   │   │   │   ├── position.py       # Position enum
│   │   │   │   ├── injury_status.py  # Injury status enum
│   │   │   │   └── api_status.py     # API status enum
│   │   │   └── interfaces/           # Repository interfaces
│   │   │       └── player_repository_interface.py
│   │   ├── repositories/             # Data Access Layer
│   │   │   ├── players/
│   │   │   │   ├── fpl_player_repository.py      # FPL API client
│   │   │   │   ├── mock_players_repository.py    # Mock data
│   │   │   │   └── __init__.py
│   │   │   └── repository_factory.py
│   │   ├── services/                 # Business Logic Layer
│   │   │   ├── players/
│   │   │   │   ├── players_business_service.py   # Business logic
│   │   │   │   ├── players_data_mapping_service.py # Data mapping
│   │   │   │   ├── players_filter_service.py     # Filtering logic
│   │   │   │   └── __init__.py
│   │   │   ├── common/
│   │   │   │   └── health_service.py
│   │   │   └── __init__.py
│   │   └── schemas/                  # DTOs (Data Transfer Objects)
│   │       ├── requests/
│   │       │   └── players_request.py
│   │       ├── responses/
│   │       │   ├── players_response.py
│   │       │   ├── health_response.py
│   │       │   └── common_response.py
│   │       └── internal/
│   │           ├── filters.py
│   │           └── cache.py
│   ├── tests/                        # Test suite
│   ├── .env                          # Environment variables
│   ├── .env.example                  # Environment template
│   ├── .gitignore
│   ├── Dockerfile                    # Docker configuration
│   ├── docker-compose.yml            # Multi-container orchestration
│   ├── Makefile                      # Build automation
│   ├── requirements.txt              # Python dependencies
│   ├── requirements-dev.txt          # Development dependencies
│   ├── requirements-prod.txt         # Production dependencies
│   ├── pyproject.toml                # Python project configuration
│   └── setup.py                      # Package setup
│
├── frontend/                         # Angular Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.ts                # Main component
│   │   │   ├── app.html              # Main template
│   │   │   ├── app.config.ts         # Angular configuration
│   │   │   ├── app.routes.ts         # Routing configuration
│   │   │   ├── config/               # Config service
│   │   │   │   ├── config.service.ts
│   │   │   │   └── app.config.ts
│   │   │   ├── environments/         # Environment configurations
│   │   │   │   ├── environment.ts
│   │   │   │   ├── environment.staging.ts
│   │   │   │   └── environment.prod.ts
│   │   │   ├── services/             # Angular services
│   │   │   │   ├── service-interfaces/
│   │   │   │   ├── implementations/
│   │   │   │   ├── mock-implementations/
│   │   │   │   └── service-factory.ts
│   │   │   ├── object-interfaces/    # TypeScript interfaces
│   │   │   ├── types/                # Type definitions
│   │   │   ├── player-card/          # Component: Player card
│   │   │   └── team-display/         # Component: Team display
│   │   ├── index.html                # HTML entry point
│   │   └── styles.css                # Global styles
│   ├── public/                       # Static assets
│   │   ├── favicon.ico               # Premier League logo
│   │   └── icons/
│   ├── angular.json                  # Angular workspace configuration
│   ├── package.json                  # Node.js dependencies
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── tsconfig.app.json
│   ├── tsconfig.spec.json
│   └── README.md                     # Frontend documentation
│
├── .git/                             # Git repository
├── .gitignore                        # Git ignore rules
├── .vscode/                          # VS Code settings
├── .idea/                            # PyCharm/IntelliJ settings
└── README.md                         # This file
```

---

## Configuration

### Backend Configuration

**Environment Variables (`.env`):**

```env
# Application
APP_NAME=FPL Optimizer API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:4200,http://localhost:3000

# FPL API
FPL_API_BASE_URL=https://fantasy.premierleague.com/api
FPL_API_TIMEOUT=30
FPL_API_MAX_RETRIES=3

# Cache (Redis)
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Frontend Configuration

**Environment Files:**

- `src/environments/environment.ts` - Development
- `src/environments/environment.staging.ts` - Staging
- `src/environments/environment.prod.ts` - Production

**Configuration Structure:**

```typescript
import { AppConfig } from "../app/config/app.config";

export const environment: AppConfig = {
  production: false,
  api: {
    baseUrl: 'http://localhost:8000/api/v1',
    timeout: 30000,
    retryAttempts: 3
  },
  features: {
    enableAdvancedOptimization: true,
    enablePlayerComparison: false,
    enableMockData: false
  },
  logging: {
    level: 'debug',
    enableConsoleLogging: true
  }
};
```

---

## Development

### Backend Development

#### Run with Auto-Reload

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Run Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

#### Code Quality

```bash
# Linting
pylint app/

# Type checking
mypy app/

# Format code
black app/
```

#### Using Makefile

```bash
make run       # Start development server
make test      # Run tests
make lint      # Run linters
make format    # Format code
make clean     # Clean cache files
```

### Frontend Development

#### Run Development Server

```bash
cd frontend
ng serve
```

With custom port:
```bash
ng serve --port 4200
```

#### Run Tests

```bash
# Unit tests
ng test

# E2E tests
ng e2e
```

#### Build for Production

```bash
ng build --configuration production
```

Output will be in `dist/` directory.

#### Code Generation

```bash
# Generate component
ng generate component component-name

# Generate service
ng generate service service-name

# Generate module
ng generate module module-name
```

---

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_players.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Frontend Testing

```bash
cd frontend

# Unit tests (watch mode)
ng test

# Unit tests (single run)
ng test --watch=false

# E2E tests
ng e2e

# Test coverage
ng test --code-coverage
```

---

## Deployment

The application is deployed using modern cloud platforms with automatic CI/CD:

### Production Deployment

#### Backend (Render)

The backend API is deployed on Render using the `render.yaml` configuration:

```yaml
services:
  - type: web
    name: fpl-optimizer-api
    env: python
    plan: free
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/v1/health
```

**Environment Variables (set in Render dashboard):**
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `SECRET_KEY` (auto-generated)
- `CORS_ORIGINS=https://fpl-optimizer-eight.vercel.app,http://localhost:4200`
- `FPL_API_BASE_URL=https://fantasy.premierleague.com/api`
- Redis URL for caching

**Deployment:**
- Automatic deployment on push to `main` branch
- Health checks at `/api/v1/health`
- Free tier includes 750 hours/month

#### Frontend (Vercel)

The frontend is deployed on Vercel using the `vercel.json` configuration:

```json
{
  "buildCommand": "npm run build:prod",
  "outputDirectory": "dist/frontend/browser",
  "framework": "angular"
}
```

**Deployment:**
- Automatic deployment on push to `main` branch
- Environment-specific builds using Angular configurations
- CDN distribution with edge caching

### Manual Deployment

#### Backend (Docker)

```bash
cd backend

# Build Docker image
docker build -t fpl-optimizer-backend .

# Run container
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  fpl-optimizer-backend
```

#### Frontend (Static Hosting)

```bash
cd frontend

# Build for production
npm run build:prod

# Output in dist/frontend/browser/
# Deploy to any static hosting service
```

### Environment Configuration

**Backend Production Variables:**
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `CORS_ORIGINS` - Include all frontend domains
- `REDIS_URL` - For production caching
- `SECRET_KEY` - For JWT tokens

**Frontend Production Variables:**
- Set in `src/environments/environment.prod.ts`
- `production: true`
- `api.baseUrl: 'https://fpl-optimizer-api.onrender.com/api/v1'`
- `features.enableMockData: false`

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Commit your changes**: `git commit -m "Add your feature"`
4. **Push to the branch**: `git push origin feature/your-feature`
5. **Open a Pull Request**

### Code Style

- **Backend**: Follow PEP 8, use `black` for formatting
- **Frontend**: Follow Angular style guide, use Prettier
- **Commits**: Use conventional commit messages

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Fantasy Premier League** - Official FPL API
- **FastAPI** - Modern Python web framework
- **Angular** - Frontend framework
- **Tailwind CSS** - Utility-first CSS framework

---

## Support

For questions or issues:

1. Check the [API Documentation](http://localhost:8000/docs)
2. Review existing [Issues](../../issues)
3. Create a [New Issue](../../issues/new)

---

## Security & Authentication

The FPL Optimizer API uses a **public API model** for read-only endpoints:

- ✅ **Public Endpoints**: `/players`, `/teams` endpoints are accessible without authentication
- ✅ **CORS Protection**: Configured to allow requests from authorized frontend domains
- ✅ **Rate Limiting**: Built-in throttling via Render free tier limits
- ✅ **Security Headers**: X-Content-Type-Options, X-Frame-Options, HSTS
- 🔐 **Future**: User authentication for saved teams and preferences using JWT tokens

This approach is appropriate for a public-facing application that uses publicly available FPL data.

---

## Roadmap

- [x] ✅ Transfer optimization using CVXPY
- [x] ✅ Fixture difficulty analysis and expected points calculation
- [x] ✅ Production deployment (Render + Vercel)
- [x] ✅ Redis caching in production
- [ ] 🚧 Interactive formation builder with drag-and-drop
- [ ] 🚧 User authentication and saved teams (JWT-based)
- [ ] 🚧 Historical performance tracking and analytics
- [ ] 🚧 Machine learning-based points prediction
- [ ] 🚧 Progressive Web App (PWA) for mobile
- [ ] 🚧 PostgreSQL for user data persistence
- [ ] 🚧 Real-time price change alerts
- [ ] 🚧 League mini-leagues comparison

---

**Happy Optimizing!** ⚽
