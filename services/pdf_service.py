from pypdf import PdfReader, PdfWriter

def load_reader(pdf_path):
    return PdfReader(pdf_path)

def add_page(writer, page, rotate=False):
    if rotate:
        page = page.rotate(180)
    writer.add_page(page)
