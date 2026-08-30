from fastapi import APIRouter
from app.modules.ragforge.services.chunkers.registry import list_chunkers

router = APIRouter()


@router.get("")
async def get_chunkers():
    return list_chunkers()
