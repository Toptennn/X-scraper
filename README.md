# X Scraper Full-Stack App

This project contains a FastAPI backend and Next.js frontend for scraping X (Twitter) using your own credentials.

## Getting Started

### Backend

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend to run on `http://localhost:8000`.
