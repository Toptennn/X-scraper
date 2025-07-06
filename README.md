# X Scraper Web

This project converts the original Streamlit based Twitter scraper into a typical web application.

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) located in the `backend/` folder.
- **Frontend**: [Next.js](https://nextjs.org/) React application located in the `frontend/` folder.

The scraping logic remains in the existing Python modules (`scraper.py`, `config.py`, etc.).

## Running the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend to run on `http://localhost:8000` and provides a simple form to trigger the scraper and display results.
