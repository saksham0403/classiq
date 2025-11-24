# ClassIQ Backend

FastAPI backend for ClassIQ classroom management system.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
DATABASE_URL=postgresql+psycopg2://postgres:<PASSWORD>@<PROJECT>.supabase.co:5432/postgres
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Start server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
