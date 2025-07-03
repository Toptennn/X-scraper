import asyncio
from backend.app.tasks import start_scrape_task, TASKS

async def dummy_run():
    await asyncio.sleep(0.1)


def test_task_registration():
    tid = start_scrape_task({'auth':'a','password':'b','mode':'timeline','screen_name':'c','count':1})
    assert tid in TASKS
