from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from typing import List

from services.file import save_file

router = APIRouter(
  prefix="/file",
  tags=["File"]
)

@router.post("/upload")
async def upload_file(
  file: UploadFile = File(...)
):
  path = save_file(file)

  return {
    "filename": file.filename,
    "path": str(path)
  }

@router.get(
  "/download/{filename}"
)
def download_file(
  filename: str
):
  path = f"uploads/{filename}"

  return FileResponse(
    path=path,
    filename=filename,
    media_type="application/octet-stream"
  )

@router.post(
  "/upload/images"
)
async def upload_images(
  files: List[UploadFile] = File(...)
):
  names = []

  for file in files:
    if file.content_type not in [
      "image/png",
      "image/jpeg"
    ]:
      raise HTTPException(
        status_code=400,
        detail="PNG/JPEGのみアップロードできます"
      )

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
      raise HTTPException(
        status_code=400,
        detail="ファイルサイズは5MB以下です"
      )
    await file.seek(0)
    
    save_file(file)
    names.append(file.filename)

  return names

@router.post(
  "/users/avatar"
)
async def upload_user_avatar(
  file: UploadFile = File(...)
):
  if file.content_type not in [
    "image/png",
    "image/jepg"
  ]:
    raise HTTPException(
      status_code=400,
      detail="PNG/JPEGのみアップロードできます"
    )
  
  content = await file.read()
  if len(content) > 2 * 1024 * 1024: # 2mb
    raise HTTPException(
      status_code=400,
      detail="ファイルサイズは2MB以下です"
    )

  await file.seek(0)
    
  path = save_file(file)
  return {
    "filename": file.filename,
    "content_type": file.content_type,
    "path": str(path)
  }
