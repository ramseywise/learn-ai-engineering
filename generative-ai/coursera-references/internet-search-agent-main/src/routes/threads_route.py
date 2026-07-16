from fastapi import APIRouter

from src import config
from src.persistence import get_checkpointer

router = APIRouter(prefix=f"/api/{config.API_VERSION}", tags=["Threads"])


@router.get("/threads/show_all")
async def list_threads():
    items = []
    async with get_checkpointer() as saver:
        async for item in saver.alist(None, filter=None):
            items.append(item)
    return items


@router.delete("/threads/delete")
async def delete_thread(thread_id: str):
    async with get_checkpointer() as saver:
        await saver.adelete_thread(thread_id)
    return {"status": "success"}
