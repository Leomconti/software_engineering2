import fitz  # PyMuPDF for PDF processing

from app.processors.file_processor import FileProcessor


class PDFProcessor(FileProcessor):
    async def generate_thumbnail(self, file_path: str, thumbnail_path: str):
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        print("Pix map here:")
        pix = page.get_pixmap()  # type: ignore
        pix.save(thumbnail_path)
