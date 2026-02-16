# ChatApp Backend

FastAPI-based backend for scalable real-time communication platform.

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache/Pub-Sub**: Redis
- **Authentication**: JWT (HS256)
- **Containerization**: Docker + Docker Compose

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── config.py        # Settings and environment config
│   │   └── security.py      # JWT and password utilities
│   ├── db/
│   │   ├── base.py          # SQLAlchemy base class
│   │   └── session.py       # Async session factory
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   ├── api/                 # REST API endpoints
│   └── websocket/           # WebSocket handlers
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Setup

### 1. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run with Docker Compose

```bash
docker-compose up -d
```

### 3. Access the API

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations (Alembic)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Authentication (TODO)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout

## Architecture Notes

- **Stateless**: No in-memory session storage
- **Async**: All I/O operations are async
- **Scalable**: Designed for horizontal scaling
- **Redis Pub/Sub**: For distributing events across instances

## Next Steps

1. Implement authentication endpoints
2. Add WebSocket handlers
3. Create message and conversation models
4. Set up Alembic migrations
5. Add comprehensive tests
