from fastapi import FastAPI

from .database import Base, engine
from .routers import auth_routes, scrape_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="X Scraper API")

app.include_router(auth_routes.router)
app.include_router(scrape_routes.router)
