# Inventory & Order Management Service

A production-ready full-stack application for managing Products and Orders for a logistics company.

## 🏗️ Project Structure

```
inventory-order-management/
├── backend/                 # FastAPI Backend
│   ├── app/                 # Application code
│   ├── alembic/             # Database migrations
│   ├── tests/               # Test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Next.js Frontend
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Full-stack orchestration
└── README.md
```

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
docker-compose up --build
# API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /products` | POST | Create product |
| `GET /products` | GET | List products (paginated) |
| `POST /orders` | POST | Create order (atomic stock management) |
| `GET /orders/{id}` | GET | Get order details |
| `PATCH /orders/{id}/status` | PATCH | Update order status |

## 🔧 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite, Alembic
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Testing**: pytest, pytest-asyncio
- **Containerization**: Docker, Docker Compose

## 🔒 Key Features

- **Atomic Stock Management**: Uses `SELECT FOR UPDATE` for PostgreSQL
- **Status Validation**: State machine for order transitions
- **Price Capture**: Historical price preserved in OrderItem
- **Eager Loading**: `lazy="selectin"` prevents N+1 queries

## 📊 Environment Variables

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | SQLite | Database connection string |
| `DEBUG` | `false` | Enable debug mode |

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## 📝 Design Decisions

1. **Monorepo Structure**: `backend/` and `frontend/` as siblings for clean separation
2. **Async SQLAlchemy**: Better performance under load
3. **Database Constraints**: `CHECK` constraint on stock_quantity as safety net
4. **SELECT FOR UPDATE**: Pessimistic locking for guaranteed consistency

## 📄 License

MIT License
