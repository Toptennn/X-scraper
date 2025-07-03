# X Scraper Dashboard (FastAPI + Next.js)

This project replaces the original Streamlit UI with a React/Next.js frontend and a FastAPI backend. It persists X/Twitter cookies in Upstash Redis and uses the `twikit` library for scraping.

## Development

1. Copy `.env.example` to `.env` and fill in your Upstash credentials.
2. Build and run with Docker Compose:

```bash
docker-compose up --build
```

The frontend will be available on `http://localhost:3000` and proxies API calls to the backend on port `8000`.

## Testing & Linting

Run linting and tests via:

```bash
make lint
make test
```

Pytest covers the service layer and Playwright can be added for end‑to‑end tests of the Next.js pages.
