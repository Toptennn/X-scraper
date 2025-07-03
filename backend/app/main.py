from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from pathlib import Path
import sys
import io
from typing import Any
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from .tasks import TASKS, start_scrape_task, TaskState

app = FastAPI(title="X Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/scrape")
async def scrape(params: dict) -> dict:
    required = {"auth", "password", "mode"}
    if not required.issubset(params.keys()):
        raise HTTPException(status_code=400, detail="Missing parameters")
    task_id = start_scrape_task(params)
    return {"task_id": task_id}


@app.get("/progress/{task_id}")
async def progress(task_id: str) -> dict:
    state = TASKS.get(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="task not found")
    return {
        "progress": state.progress,
        "tweets_collected": state.collected,
        "total_requested": state.total,
        "done": state.done,
    }


@app.get("/result/{task_id}")
async def result(task_id: str) -> Any:
    state = TASKS.get(task_id)
    if not state:
        raise HTTPException(status_code=404, detail="task not found")
    if not state.done:
        raise HTTPException(status_code=202, detail="task running")
    return state.result


@app.get("/export/{task_id}")
async def export(task_id: str, fmt: str = "csv"):
    state = TASKS.get(task_id)
    if not state or not state.done:
        raise HTTPException(status_code=404, detail="task not ready")
        import io
    df = pd.DataFrame(state.result)
    if fmt == "xlsx":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={task_id}.xlsx"},
        )
    else:
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={task_id}.csv"},
        )
