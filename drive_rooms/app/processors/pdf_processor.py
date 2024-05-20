import fitz  # PyMuPDF for PDF processing

from app.processors.file_processor import FileProcessor


class PDFProcessor(FileProcessor):
    async def generate_thumbnail(self, file_path: str, thumbnail_path: str):
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()  # type: ignore # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_pixmap

        thumbnail_path = thumbnail_path.rsplit(".", 1)[0] + ".png"  # gotta save as png ofc, otherwise breaks everything
        pix.save(thumbnail_path)
        return thumbnail_path
