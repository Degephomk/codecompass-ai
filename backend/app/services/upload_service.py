from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, BadZipFile, is_zipfile
from fastapi import HTTPException, UploadFile
from app.services.indexing_service import index_repository


BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"

UPLOADS_DIR = STORAGE_DIR / "uploads"
EXTRACTED_DIR = STORAGE_DIR / "extracted"


UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


async def handle_upload(file: UploadFile) -> dict:
    """
    Save and extract an uploaded repository ZIP file.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A file is required."
        )

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported."
        )

    project_id = str(uuid4())

    zip_path = UPLOADS_DIR / f"{project_id}.zip"
    project_dir = EXTRACTED_DIR / project_id

    # Save uploaded file
    try:
        with zip_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
    finally:
        await file.close()

    # Verify that the uploaded file is actually a ZIP
    if not is_zipfile(zip_path):
        zip_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid ZIP archive."
        )

    # Create extraction directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Safely extract ZIP contents
    try:
        with ZipFile(zip_path, "r") as archive:
            for member in archive.infolist():
                target_path = (project_dir / member.filename).resolve()

                if not str(target_path).startswith(str(project_dir.resolve())):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid ZIP archive."
                    )

            archive.extractall(project_dir)
            index_result = index_repository(
                project_path=project_dir,
                project_id=project_id,
            )

    except BadZipFile:
        zip_path.unlink(missing_ok=True)
        project_dir.rmdir()

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid ZIP archive."
        )

    return {
        "project_id": project_id,
        "filename": file.filename,
        "status": "uploaded",
        "message": "Repository uploaded and indexed successfully.",
        "file_count": index_result["file_count"],
        "chunk_count": index_result["chunk_count"],
    }
