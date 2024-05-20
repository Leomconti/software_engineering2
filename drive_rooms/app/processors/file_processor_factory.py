from app.processors.jpg_processor import JPGProcessor
from app.processors.pdf_processor import PDFProcessor
from app.processors.png_processor import PNGProcessor


class FileProcessorFactory:
    @staticmethod
    def get_processor(file_extension: str):
        if file_extension.lower() == "pdf":
            return PDFProcessor()
        elif file_extension.lower() in ["png", "jpg", "jpeg"]:
            if file_extension.lower() == "png":
                return PNGProcessor()
            else:
                return JPGProcessor()
        else:
            raise ValueError("Unsupported file type")
