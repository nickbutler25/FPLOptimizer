# FPL Optimizer API

A professional FastAPI REST API for Fantasy Premier League data optimization.

## Features

- **RESTful API**: Well-structured endpoints following REST principles
- **Dependency Injection**: Clean architecture using dependency-injector
- **Logging**: Structured JSON logging for production environments
- **Authentication**: API key-based authentication for secure access
- **Caching**: Redis caching for improved performance
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Type Safety**: Full type hints with Pydantic models
- **Docker Support**: Containerized deployment with Docker and docker-compose
- **Auto Documentation**: Interactive API docs with Swagger UI and ReDoc

## API Endpoints

### Health
- `GET /api/v1/health` - Health check endpoint

### Players
- `GET /api/v1/players` - Get all FPL players with optional filters
  - Query params: `position`, `team_id`, `min_cost`, `max_cost`
- `GET /api/v1/players/{player_id}` - Get specific player by ID
- `GET /api/v1/players/top/points` - Get top players by total points
  - Query params: `limit` (default: 10)

### Teams
- `GET /api/v1/teams/{team_id}` - Get FPL team by entry ID
  - Query params: `include_picks` (default: true)
- `GET /api/v1/teams/{team_id}/summary` - Get team summary with key statistics

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional, for caching)
- Docker & Docker Compose (for containerized deployment)

### Local Development

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run the application:**
   ```bash
   python -m app.main
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   - API: http://localhost:8000

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

```bash
# Application Settings
APP_NAME=FPL Optimizer API
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# FPL API
FPL_API_BASE_URL=https://fantasy.premierleague.com/api
FPL_API_TIMEOUT=30

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CACHE_TTL=300
```

## Authentication

All endpoints (except `/health`) require API key authentication. Include the API key in the request header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/api/v1/players
```

## Example Usage

### Get All Players
```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/players"
```

### Get Players by Position
```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/players?position=Midfielder&min_cost=5.0&max_cost=10.0"
```

### Get Team by ID
```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/teams/123456"
```

### Get Top Players
```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/players/top/points?limit=20"
```

## Architecture

```
backend/
├── app/
│   ├── api/              # API layer
│   │   ├── v1/
│   │   │   ├── endpoints/  # API endpoints
│   │   │   └── router.py   # API router
│   │   ├── dependencies.py # FastAPI dependencies
│   │   └── middleware.py   # Custom middleware
│   ├── core/             # Core configuration
│   │   ├── config.py       # Settings management
│   │   ├── container.py    # DI container
│   │   ├── exceptions.py   # Custom exceptions
│   │   ├── logging.py      # Logging setup
│   │   └── security.py     # Authentication
│   ├── infrastructure/   # Infrastructure layer
│   │   ├── cache/          # Cache implementations
│   │   └── http/           # HTTP clients
│   ├── models/           # Domain models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # API schemas
│   ├── services/         # Business logic layer
│   └── main.py          # Application entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Technology Stack

- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation using Python type hints
- **httpx**: Async HTTP client for external API calls
- **dependency-injector**: Dependency injection framework
- **Redis**: In-memory caching
- **python-jose**: JWT token handling
- **tenacity**: Retry logic for resilient API calls
- **python-json-logger**: Structured logging

## Development

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
```

### Linting
```bash
ruff check app/
```

### Type Checking
```bash
mypy app/
```

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    {
      "field": "field_name",
      "message": "Detailed error message",
      "type": "error_type"
    }
  ]
}
```

## Performance

- **Caching**: Redis caching with configurable TTL (default: 5 minutes)
- **Retry Logic**: Automatic retries for failed FPL API requests
- **Async/Await**: Fully asynchronous for optimal performance
- **Connection Pooling**: Efficient HTTP connection management

## License

MIT License
