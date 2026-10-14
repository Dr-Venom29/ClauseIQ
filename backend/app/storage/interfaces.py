from abc import ABC, abstractmethod

class IStorageProvider(ABC):
    @abstractmethod
    def save_file(self, file_content: bytes, filename: str, custom_id: str = None) -> str:
        """
        Saves the file content and returns the storage path or identifier.
        """
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """
        Deletes the file and returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_file_path(self, storage_path: str) -> str:
        """
        Returns a local filepath or temporary access URL to read/parse the file.
        """
        pass

    @abstractmethod
    def file_exists(self, storage_path: str) -> bool:
        """
        Returns True if the file exists in the storage provider, False otherwise.
        """
        pass
