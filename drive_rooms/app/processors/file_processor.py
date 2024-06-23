from abc import ABC, abstractmethod


class FileProcessor(ABC):
    @abstractmethod
    async def generate_thumbnail(self, file_path: str, thumbnail_path: str) -> str:
        pass
