.PHONY: lint test backend frontend

lint:
ruff .
prettier -c frontend

test:
pytest -q

backend:
docker build -t xscraper-backend ./backend

frontend:
docker build -t xscraper-frontend ./frontend
