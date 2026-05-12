# CV API

A production-ready FastAPI backend for serving CV/portfolio content through REST endpoints. Designed for deployment in containerized environments and cloud platforms.

## Features

- **Markdown-to-HTML conversion** with XSS protection
- **Multiple output formats** (raw markdown, sanitized HTML, metadata)
- **Docker-ready** with multi-stage builds and non-root user
- **CI/CD pipeline** with GitHub Actions for automated testing and Docker Hub publishing
- **Structured logging** supporting JSON for production aggregation
- **CORS support** for frontend integration
- **Health checks** for container orchestration
- **OpenAPI documentation** (auto-generated, disabled in production)

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements/dev.txt

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the Makefile
make dev
```

### Docker

```bash
# Build image
docker build -t cv-api:latest .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data cv-api:latest
```

### Using Docker Hub

```bash
docker pull pzzt/cv-api:latest
docker run -p 8000:8000 -v $(pwd)/data:/app/data pzzt/cv-api:latest
```

## API Endpoints

### Health Check

```
GET /api/health
```

Returns service health status, version, and environment.

### Get Raw Markdown

```
GET /api/cv/raw
```

Returns raw markdown content with file metadata.

**Response:**
```json
{
  "content": "# Your CV content...",
  "metadata": {
    "filename": "mycv.md",
    "path": "/app/data/mycv.md",
    "size_bytes": 1234,
    "last_modified": "2026-05-12T10:00:00Z",
    "parser_status": "ready",
    "content_length": 1234,
    "line_count": 42,
    "version": "1.0.0"
  }
}
```

### Get HTML

```
GET /api/cv/html
```

Returns sanitized HTML ready for display.

### Get Metadata

```
GET /api/cv/metadata
```

Returns file metadata without content (more efficient).

## Configuration

Configure via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `CV_API_APP_ENVIRONMENT` | `development` | Environment (development, staging, production) |
| `CV_API_MARKDOWN_PATH` | `data/mycv.md` | Path to markdown CV file |
| `CV_API_CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `CV_API_LOG_LEVEL` | `INFO` | Logging level |
| `CV_API_LOG_FORMAT` | `json` | Log format (json or plain) |
| `CV_API_ENABLE_HOT_RELOAD` | `false` | Enable automatic file reload on changes |

## Project Structure

```
myCV/
├── app/
│   ├── api/                 # API aggregation layer
│   ├── core/                # Configuration
│   │   └── config.py        # Settings management
│   ├── dependencies/        # FastAPI dependencies
│   ├── routers/             # API endpoints
│   │   ├── cv.py            # CV content routes
│   │   └── health.py        # Health check route
│   ├── schemas/             # Pydantic models
│   │   └── cv.py            # Response schemas
│   ├── services/            # Business logic
│   │   └── markdown_service.py
│   ├── utils/               # Utilities
│   │   └── logging.py       # Logging configuration
│   └── main.py              # Application entry point
├── data/
│   └── mycv.md              # Your CV content
├── tests/                   # Test suite
├── requirements/            # Dependency specifications
├── .github/workflows/       # CI/CD pipelines
├── Dockerfile               # Multi-stage production build
└── pyproject.toml           # Project configuration
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term

# Run specific test file
pytest tests/test_services.py -v
```

### Code Quality

```bash
# Lint with ruff
ruff check app/

# Format code
ruff format app/

# Type checking
mypy app/
```

### Running in Development Mode

```bash
# With hot reload and debug logs
CV_API_LOG_LEVEL=DEBUG CV_API_ENABLE_HOT_RELOAD=true \
    uvicorn app.main:app --reload --host 0.0.0.0
```

## Deployment

### Production Server

The Docker image uses Gunicorn with Uvicorn workers:

```bash
gunicorn --bind 0.0.0.0:8000 \
         --workers 4 \
         --worker-class uvicorn.workers.UvicornWorker \
         app.main:app
```

### VPS Deployment

```bash
# Pull image
docker pull pzzt/cv-api:latest

# Run with restart policy
docker run -d \
  --name cv-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /path/to/cv/data:/app/data \
  pzzt/cv-api:latest
```

### Behind Nginx Reverse Proxy

```nginx
location /api/ {
    proxy_pass http://localhost:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Kubernetes (Optional)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cv-api-config
data:
  CV_API_APP_ENVIRONMENT: "production"
  CV_API_LOG_FORMAT: "json"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cv-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cv-api
  template:
    metadata:
      labels:
        app: cv-api
    spec:
      containers:
      - name: cv-api
        image: pzzt/cv-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: cv-api-config
        volumeMounts:
        - name: cv-data
          mountPath: /app/data
      volumes:
      - name: cv-data
        configMap:
          name: cv-content
```

## Security

- **HTML sanitization** using `nh3` (rust-based, OWASP compliant)
- **Non-root container user** (uid 1000)
- **CORS configuration** for frontend access control
- **No unnecessary dependencies** reducing attack surface
- **Read-only filesystem** where possible (except data directory)

## CI/CD

The GitHub Actions workflow:

1. **Lint**: Runs ruff for code quality checks
2. **Test**: Executes pytest with coverage reporting
3. **Build**: Creates Docker image with build caching
4. **Publish**: Pushes to Docker Hub on main branch

### Required Secrets

- `DOCKER_HUB_USERNAME`: Docker Hub username
- `DOCKER_HUB_TOKEN`: Docker Hub access token

## Architecture Decisions

### Why nh3 instead of bleach?

`nh3` is a Python binding for the Rust `ammonia` library. It's:
- **Faster**: Rust-based performance
- **Safer**: Actively maintained for security
- **Simpler**: No extra dependencies like Jinja2

### Why FastAPI instead of Flask?

- **Native async support** for better performance
- **Automatic OpenAPI docs** during development
- **Pydantic integration** for request/response validation
- **Type hints** for better IDE support

### Why separate service layer?

- **Testability**: Business logic isolated from framework
- **Reusability**: Can be used outside FastAPI context
- **Maintainability**: Clear separation of concerns

### Why structured logging?

JSON logs enable:
- **Log aggregation**: Easy parsing by ELK, Loki, CloudWatch
- **Structured queries**: Filter by specific fields
- **Consistency**: Same format across all services

## License

MIT

## Author

Andrea Pozzato

## Links

- **Docker Hub**: https://hub.docker.com/r/pzzt/cv-api
- **GitHub**: https://github.com/pzzt/myCV
