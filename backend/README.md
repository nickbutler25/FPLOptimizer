# FPL Optimizer - Backend API

> FastAPI-based REST API for Fantasy Premier League optimization with Clean Architecture

---

## Overview

The backend is a modern, async-first REST API built with FastAPI that provides:

- Real-time player data from the official FPL API
- Advanced filtering and search capabilities
- Smart caching with configurable TTL
- Comprehensive health monitoring
- OpenAPI/Swagger documentation
- Clean Architecture with clear separation of concerns

---

## Architecture

```
API Layer (FastAPI)
    ├── Endpoints (HTTP handlers)
    ├── Request/Response DTOs
    └── Middleware & Exception Handling
         ↓
Business Logic Layer
    ├── Data Mapping Service
    ├── Filtering Service
    └── Validation & Business Rules
         ↓
Repository Layer
    ├── FPL API Client (with caching)
    ├── Retry Logic
    └── Data Access Abstraction
         ↓
Domain Layer
    ├── Entities (Player, etc.)
    ├── Enums (Position, InjuryStatus)
    └── Repository Interfaces
         ↓
External Data Source (FPL API)
```

---

## Prerequisites

- **Python 3.11+**
- **pip** (comes with Python)
- **virtualenv** (recommended)

---

## Quick Start

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (includes testing and linting tools):
```bash
pip install -r requirements-dev.txt
```

### 3. Configure Environment

Create a `.env` file in the `backend/` directory:

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
RELOAD=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:5000

# FPL API
FPL_API_BASE_URL=https://fantasy.premierleague.com/api
FPL_API_TIMEOUT=30
FPL_API_MAX_RETRIES=3
FPL_CACHE_TTL=3600

# Cache
CACHE_ENABLED=true
CACHE_TYPE=memory
CACHE_TTL=3600

# Optional: Redis
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=false

# Optional: Database
DATABASE_URL=postgresql://user:password@localhost:5432/fpl_optimizer
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                       # Application entry point
│   ├── api/                          # API Layer
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── players.py        # Players API endpoints
│   │   │   │   └── health.py         # Health check endpoints
│   │   │   └── router.py             # API v1 router
│   │   ├── dependencies.py           # Shared dependencies
│   │   ├── exceptions.py             # Exception handlers
│   │   └── middleware.py             # API middleware
│   ├── core/                         # Core Configuration
│   │   ├── config.py                 # Settings management (Pydantic)
│   │   ├── container.py              # Dependency injection
│   │   ├── exceptions.py             # Custom exceptions
│   │   ├── logging.py                # Logging setup
│   │   ├── middleware.py             # Core middleware
│   │   └── security.py               # Security utilities
│   ├── domain/                       # Domain Layer
│   │   ├── entities/
│   │   │   └── player.py             # Player domain entity
│   │   ├── enums/
│   │   │   ├── position.py           # Position enum
│   │   │   ├── injury_status.py      # Injury status enum
│   │   │   └── api_status.py         # API status enum
│   │   └── interfaces/
│   │       └── player_repository_interface.py
│   ├── repositories/                 # Data Access Layer
│   │   ├── players/
│   │   │   ├── fpl_player_repository.py      # FPL API integration
│   │   │   ├── mock_players_repository.py    # Mock data (testing)
│   │   │   └── __init__.py
│   │   └── repository_factory.py
│   ├── services/                     # Business Logic Layer
│   │   ├── players/
│   │   │   ├── players_business_service.py   # Orchestration
│   │   │   ├── players_data_mapping_service.py # Data mapping
│   │   │   ├── players_filter_service.py     # Filtering logic
│   │   │   └── __init__.py
│   │   ├── common/
│   │   │   └── health_service.py
│   │   └── __init__.py
│   └── schemas/                      # DTOs
│       ├── requests/
│       │   └── players_request.py
│       ├── responses/
│       │   ├── players_response.py
│       │   ├── health_response.py
│       │   └── common_response.py
│       └── internal/
│           ├── filters.py
│           └── cache.py
├── tests/                            # Test suite
├── .env                              # Environment variables
├── .env.example                      # Environment template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt                  # Production dependencies
├── requirements-dev.txt              # Development dependencies
├── requirements-prod.txt
├── pyproject.toml
└── setup.py
```

---

## API Endpoints

### Root Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root information |
| `GET` | `/health` | Simple health check |

### Players API

**Base Path:** `/api/v1/players`

#### Get All Players (with filters)

```http
GET /api/v1/players
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `positions` | string[] | Filter by position (GKP, DEF, MID, FWD) |
| `teams` | string[] | Filter by team name |
| `min_cost` | float | Minimum player cost (£M) |
| `max_cost` | float | Maximum player cost (£M) |
| `min_points` | int | Minimum total points |
| `max_points` | int | Maximum total points |
| `min_form` | float | Minimum form rating |
| `available_only` | bool | Only available players (not injured) |
| `min_minutes` | int | Minimum minutes played |
| `min_selected_percent` | float | Minimum ownership % |
| `max_selected_percent` | float | Maximum ownership % |
| `search_term` | string | Search player names |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/players?positions=FWD&min_cost=5.0&max_cost=10.0&available_only=true"
```

**Response:**

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

#### Get Single Player

```http
GET /api/v1/players/{player_id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `player_id` | int | FPL Player ID |

**Response:**

```json
{
  "status": "success",
  "player": {
    "id": 123,
    "name": "Example Player",
    ...
  }
}
```

### Health Check API

**Base Path:** `/api/v1/health`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health/` | Comprehensive health check |
| `GET` | `/api/v1/health/simple` | Simple health check |
| `GET` | `/api/v1/health/status` | Detailed status info |
| `GET` | `/api/v1/health/ready` | Kubernetes readiness probe |
| `GET` | `/api/v1/health/live` | Kubernetes liveness probe |
| `GET` | `/api/v1/health/metrics` | Prometheus metrics |

---

## Configuration

### Environment Variables

**Required:**

- `APP_NAME` - Application name
- `FPL_API_BASE_URL` - FPL API base URL (default: https://fantasy.premierleague.com/api)

**Optional:**

- `DEBUG` - Enable debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `CACHE_ENABLED` - Enable caching (default: true)
- `CACHE_TYPE` - Cache type: memory or redis (default: memory)
- `CACHE_TTL` - Cache TTL in seconds (default: 3600)
- `REDIS_URL` - Redis connection URL
- `DATABASE_URL` - PostgreSQL connection URL

### Configuration via Pydantic

Settings are managed via Pydantic models in [app/core/config.py](app/core/config.py):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FPL Optimizer API"
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
```

---

## Development

### Run with Auto-Reload

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=app --cov-report=html
```

### Code Quality

**Linting:**
```bash
pylint app/
```

**Type Checking:**
```bash
mypy app/
```

**Format Code:**
```bash
black app/
```

**Sort Imports:**
```bash
isort app/
```

### Using Makefile

```bash
make run       # Start development server
make test      # Run tests
make lint      # Run linters
make format    # Format code
make clean     # Clean cache files
make docker    # Build Docker image
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_players.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

Coverage report will be in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

---

## Docker

### Build Image

```bash
docker build -t fpl-optimizer-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env fpl-optimizer-backend
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Deployment

### Production Setup

1. **Set Environment Variables:**

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
REDIS_ENABLED=true
REDIS_URL=redis://production-redis:6379
DATABASE_URL=postgresql://user:pass@db:5432/fpl_optimizer
```

2. **Install Production Dependencies:**

```bash
pip install -r requirements-prod.txt
```

3. **Run with Gunicorn:**

```bash
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Health Checks

For Kubernetes/Docker health checks:

- **Liveness:** `GET /api/v1/health/live`
- **Readiness:** `GET /api/v1/health/ready`

### Monitoring

Prometheus metrics available at:
```
GET /api/v1/health/metrics
```

---

## Design Patterns

### Clean Architecture

- **API Layer** - HTTP handling only, minimal logic
- **Business Layer** - Core business logic and orchestration
- **Repository Layer** - Pure data access, no business logic
- **Domain Layer** - Entities and interfaces

### Key Patterns

- **Repository Pattern** - Abstract data access
- **Dependency Injection** - Loose coupling via containers
- **DTO Pattern** - Separate API contracts from domain models
- **Cache-aside** - Check cache, fallback to source, update cache
- **Retry with Backoff** - Resilient external API calls

---

## Troubleshooting

### Common Issues

**Issue: Module not found**
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**Issue: Port already in use**
```bash
# Solution: Use different port
uvicorn app.main:app --port 8001
```

**Issue: FPL API timeout**
```bash
# Solution: Increase timeout in .env
FPL_API_TIMEOUT=60
```

**Issue: Cache not working**
```bash
# Solution: Enable cache in .env
CACHE_ENABLED=true
```

---

## Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

**Backend-specific guidelines:**

- Follow PEP 8 style guide
- Use `black` for code formatting
- Use `mypy` for type checking
- Write tests for all new features
- Update API documentation (docstrings)

---

## License

MIT License - See [LICENSE](../LICENSE)

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FPL API Documentation](https://fantasy.premierleague.com/api/)
