# UTM Backend API

🚁 **Unmanned Traffic Management (UTM) System Backend** - A comprehensive FastAPI-based backend for managing drone operations, flight plans, and airspace coordination.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 🎯 Overview

This UTM backend provides a complete API for managing:

- **👥 Multi-role User Management** (Authority Admins, Organization Admins, Pilots)
- **🏢 Organization Management** with hierarchical permissions
- **🚁 Drone Registration** and assignment systems
- **✈️ Flight Plan Management** with approval workflows
- **🚫 No-Fly Zone (NFZ)** enforcement and monitoring
- **📡 Real-time Telemetry** tracking via WebSockets
- **🔒 JWT-based Authentication** with role-based access control

## 🏗️ Architecture

### User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Authority Admin** | Full system access, manage NFZs, approve all flights |
| **Organization Admin** | Manage organization users/drones, approve org flights |
| **Organization Pilot** | Submit flights for assigned drones within organization |
| **Solo Pilot** | Manage personal drones and submit flights |

### Core Models

- **Users** - Authentication and role-based access
- **Organizations** - Multi-tenant structure with admins
- **Drones** - Equipment registration and status tracking  
- **Flight Plans** - Mission planning with waypoints and approval workflow
- **Restricted Zones** - No-fly zones with geometric boundaries
- **Telemetry** - Real-time flight tracking data

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd utm-backend
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Option A: Using Docker
   docker-compose up -d db
   
   # Option B: Local PostgreSQL
   createdb utm_db
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🐳 Docker Deployment

### Development
```bash
# Start database only
docker-compose up -d db

# Run migrations
alembic upgrade head

# Start API locally
uvicorn app.main:app --reload
```

### Production
```bash
# Start all services
docker-compose up -d

# The API will be available at http://localhost:8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://utm_user:utm_password@localhost/utm_db
POSTGRES_SERVER=localhost
POSTGRES_USER=utm_user
POSTGRES_PASSWORD=utm_password
POSTGRES_DB=utm_db

# Security
SECRET_KEY=your_super_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Initial Admin User
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
FIRST_SUPERUSER_FULL_NAME=Authority Admin
FIRST_SUPERUSER_IIN=000000000000

# WebSocket
WS_TELEMETRY_PATH=/ws/telemetry
```

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/register/solo-pilot` - Register solo pilot
- `POST /api/v1/auth/register/organization-admin` - Register organization + admin
- `POST /api/v1/auth/register/organization-pilot` - Register organization pilot
- `POST /api/v1/auth/login/access-token` - Login (get JWT token)

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update own profile
- `GET /api/v1/users/` - List all users (Admin only)

### Organizations
- `GET /api/v1/organizations/` - List organizations
- `GET /api/v1/organizations/{id}` - Get organization details
- `GET /api/v1/organizations/{id}/users` - List organization users
- `GET /api/v1/organizations/{id}/drones` - List organization drones

### Drones
- `POST /api/v1/drones/` - Register new drone
- `GET /api/v1/drones/my` - List user's drones
- `GET /api/v1/drones/{id}` - Get drone details
- `PUT /api/v1/drones/{id}` - Update drone
- `POST /api/v1/drones/{id}/assign-user` - Assign pilot to drone (Org Admin)

### Flight Plans
- `POST /api/v1/flights/` - Submit flight plan
- `GET /api/v1/flights/my` - List user's flights
- `GET /api/v1/flights/organization` - List organization flights (Org Admin)
- `PUT /api/v1/flights/{id}/status` - Update flight status (Admin approval)
- `PUT /api/v1/flights/{id}/start` - Start approved flight
- `PUT /api/v1/flights/{id}/cancel` - Cancel flight

### No-Fly Zones
- `POST /api/v1/admin/nfz/` - Create NFZ (Authority Admin)
- `GET /api/v1/nfz/` - List active NFZs (public)
- `PUT /api/v1/admin/nfz/{id}` - Update NFZ
- `DELETE /api/v1/admin/nfz/{id}` - Delete NFZ

### Real-time Telemetry
- `WS /ws/telemetry` - WebSocket for live flight tracking

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Get Token**: POST to `/api/v1/auth/login/access-token`
2. **Use Token**: Include in headers: `Authorization: Bearer <token>`
3. **Token Expiry**: Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`

### Example Usage

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis"

# Use token
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your-token>"
```

## 📊 Database Schema

### Key Relationships
- Users belong to Organizations (optional for solo pilots)
- Drones are owned by Users or Organizations
- Flight Plans link Users, Drones, and Waypoints
- Telemetry tracks real-time flight data
- Restricted Zones define no-fly areas

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🧪 Testing

### Run Comprehensive Database Tests
```bash
python test_database_full.py
```

This comprehensive test suite:
- ✅ Creates full-scale test data (users, orgs, drones, flights)
- 🧪 Tests all CRUD operations and relationships
- ⚡ Measures performance with complex queries
- 🧹 Cleans up all test data automatically
- 📊 Generates detailed test reports

### Manual API Testing
```bash
# Install development dependencies
pip install pytest httpx

# Run tests (if test files exist)
pytest

# Or test with curl/Postman using the Swagger docs
```

## 🔄 Real-time Features

### WebSocket Telemetry
Connect to `/ws/telemetry` to receive live flight updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/telemetry?token=<jwt-token>');
ws.onmessage = (event) => {
  const telemetry = JSON.parse(event.data);
  console.log('Flight update:', telemetry);
};
```

Telemetry messages include:
- Flight ID and drone ID
- Current position (lat/lon/altitude)
- Speed and heading
- Flight status (ON_SCHEDULE, NFZ_ALERT, etc.)

## 🛠️ Development

### Project Structure
```
utm-backend/
├── app/
│   ├── api/           # API routes and dependencies
│   ├── core/          # Configuration and security
│   ├── crud/          # Database operations
│   ├── db/            # Database connection and utilities
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   └── services/      # Business logic
├── alembic/           # Database migrations
├── tests/             # Test files
└── requirements.txt   # Dependencies
```

### Adding New Features

1. **Create Model**: Add SQLAlchemy model in `app/models/`
2. **Create Schema**: Add Pydantic schemas in `app/schemas/`
3. **Create CRUD**: Add database operations in `app/crud/`
4. **Create Routes**: Add API endpoints in `app/api/routers/`
5. **Run Migration**: `alembic revision --autogenerate -m "Add feature"`

### Code Style
- Follow PEP 8
- Use type hints
- Document complex functions
- Keep business logic in services

## 🚀 Production Deployment

### Security Checklist
- [ ] Change default `SECRET_KEY`
- [ ] Use strong database passwords
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Monitor logs and metrics

### Scaling Considerations
- Use connection pooling for database
- Consider Redis for caching
- Use async workers (e.g., Celery) for background tasks
- Set up load balancing for multiple instances
- Monitor performance and add database indexes as needed

## 📈 Monitoring & Logging

### Health Checks
- `GET /api/v1/health` - Basic health status
- Database connectivity is tested on startup

### Logging
- Application logs to stdout
- Database query logging available
- WebSocket connection logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Run the database test suite: `python test_database_full.py`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Database Connection Errors**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database credentials

**Migration Errors**
- Run `alembic upgrade head`
- Check for conflicting migrations
- Ensure database schema is clean

**JWT Token Issues**
- Check SECRET_KEY configuration
- Verify token hasn't expired
- Ensure proper Authorization header format

### Getting Help
- Check the [Issues](link-to-issues) page
- Review API documentation at `/docs`
- Run the test suite to verify setup

---

**Built with ❤️ for safe drone operations**
