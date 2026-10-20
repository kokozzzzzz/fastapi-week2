from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter,File,HTTPException,UploadFile


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

MAX_FILE_SIZE = 5*1024*1024

ALLOWED_EXIENSIONS = {".txt",".md",".pdf"}



@router.post("/",status_code=201)
async def upload_file(
    file: UploadFile = File(...)
):
    original_name = file.filename or "unnamed"
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_EXIENSIONS:
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="不支持该文件格式",
        )

    stored_name = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / stored_name
    size = 0

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(1024*1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="文件超过5MB，文件过大",
                    )

                output.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return {
        "filename": original_name,
        "stored_as": stored_name,
        "size_bytes": size,
    }

