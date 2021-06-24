from fastapi import APIRouter

router = APIRouter()


@router.get("/update")
async def update_admin():
    return {"message": "Admin getting schwifty"}