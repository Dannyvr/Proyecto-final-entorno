from typing import List
from fastapi import APIRouter

router = APIRouter()

@router.get("/zones/")
async def get_zones():
    """
    Retrieve a list of all zones.
    """
    return "List of zones"
