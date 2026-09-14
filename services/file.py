from pathlib import Path
import shutil

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_file(file):
  file_path = UPLOAD_DIR / file.filename

  with open(file_path, "wb") as buffer: # wb 写二进制
    shutil.copyfileobj(file.file, buffer) # 把上传文件流复制到磁盘

  return file_path