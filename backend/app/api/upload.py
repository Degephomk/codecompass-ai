from fastapi import APIRouter, UploadFile, File

from app.services.upload_service import handle_upload


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_repository(
    file: UploadFile = File(...)
):
    return await handle_upload(file)
