import os
import shutil
from fastapi import UploadFile
from app.config import settings

os.makedirs(settings.STORAGE_DIR, exist_ok=True)

class StorageService:
    @staticmethod
    def save_upload_file(upload_file: UploadFile, subfolder: str, filename: str) -> str:
        target_dir = os.path.join(settings.STORAGE_DIR, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path

storage_service = StorageService()
