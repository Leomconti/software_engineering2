from PIL import Image

from app.processors.file_processor import FileProcessor


class PNGProcessor(FileProcessor):
    async def generate_thumbnail(self, file_path: str, thumbnail_path: str):
        image = Image.open(file_path)
        image.thumbnail((100, 100))
        image.save(thumbnail_path)
        return thumbnail_path
