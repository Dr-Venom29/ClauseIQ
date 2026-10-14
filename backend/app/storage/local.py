import os
from app.storage.interfaces import IStorageProvider

class LocalStorageProvider(IStorageProvider):
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_content: bytes, filename: str, custom_id: str = None) -> str:
        prefix = f"{custom_id}_" if custom_id else ""
        storage_filename = f"{prefix}{filename}"
        storage_path = os.path.join(self.upload_dir, storage_filename)
        with open(storage_path, "wb") as f:
            f.write(file_content)
        return storage_path

    def delete_file(self, storage_path: str) -> bool:
        if self.file_exists(storage_path):
            try:
                os.remove(storage_path)
                return True
            except OSError:
                return False
        return False

    def get_file_path(self, storage_path: str) -> str:
        return os.path.abspath(storage_path)

    def file_exists(self, storage_path: str) -> bool:
        return os.path.exists(storage_path)
