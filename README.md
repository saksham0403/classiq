# ClassIQ - AI-Powered Classroom Assistant

A full-stack web application for teachers to manage classrooms, create assignments, and get insights into student performance, while students can submit assignments and view their learning progress.

## Tech Stack

- **Backend**: FastAPI (Python 3.x), SQLAlchemy, Alembic, JWT Auth
- **Frontend**: React + TypeScript, Vite, Tailwind CSS, Recharts
- **Database**: Supabase PostgreSQL

## Project Structure

```
classiq/
├── backend/
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── auth.py       # Authentication utilities
│   │   ├── grading.py   # Auto-grading logic
│   │   ├── database.py  # Database connection
│   │   └── main.py       # FastAPI app
│   ├── alembic/          # Database migrations
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/        # React pages
    │   ├── services/     # API client
    │   ├── utils/        # Utilities (auth)
    │   └── types/        # TypeScript types
    └── package.json
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account (for PostgreSQL database)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```env
DATABASE_URL=postgresql+psycopg2://postgres:<PASSWORD>@<PROJECT>.supabase.co:5432/postgres
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
```

Replace `<PASSWORD>` and `<PROJECT>` with your Supabase credentials.

5. Run database migrations:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Features

### Teacher Features
- Sign up / Log in
- Create and manage classrooms
- Add students to classrooms
- Create assignments with questions
- View classroom analytics (topic performance, hardest questions)
- View student summaries

### Student Features
- Sign up / Log in
- View assignments for enrolled classrooms
- Submit answers to assignments
- View submission results with auto-grading
- View learning summary (strengths, weak topics, recommended practice)

## API Endpoints

### Auth
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user

### Classrooms
- `POST /classrooms/` - Create classroom (teacher only)
- `GET /classrooms/` - List classrooms (teacher only)
- `POST /classrooms/{id}/students` - Add student (teacher only)
- `GET /classrooms/{id}/students` - List students

### Assignments
- `POST /assignments/` - Create assignment (teacher only)
- `GET /assignments/classrooms/{id}/assignments` - List assignments
- `GET /assignments/{id}` - Get assignment with questions
- `POST /assignments/{id}/questions` - Add question (teacher only)

### Submissions
- `POST /assignments/{id}/submissions` - Submit assignment (student only)

### Analytics
- `GET /classrooms/{id}/analytics` - Classroom analytics (teacher only)
- `GET /students/{id}/summary` - Student summary

## Grading Logic

The system uses deterministic rules for auto-grading:

- **Numeric**: Compares float values within tolerance (1e-3)
- **Algebra**: Uses SymPy to test expression/equation equivalence
- **Short Answer**: Text similarity using Jaccard similarity (threshold: 0.7)
- **MCQ**: Exact match comparison

## Development Notes

- The backend uses SQLAlchemy ORM with Alembic for migrations
- JWT tokens are stored in localStorage on the frontend
- CORS is enabled for localhost:5173 and localhost:3000
- All API responses use Pydantic schemas for validation

## Next Steps

To extend the MVP:
- Add file upload support for assignments
- Implement OCR for handwritten answers
- Add LLM-based grading for open-ended questions
- Implement real-time notifications
- Add email notifications for assignment deadlines

