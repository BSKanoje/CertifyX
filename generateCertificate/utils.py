from io import BytesIO
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import qrcode
from pdf2image import convert_from_path


def generate_qr_image(data):
    qr = qrcode.make(data)
    return qr.convert('RGB')


def generate_qr_image(data):
    qr = qrcode.make(data)
    return qr.convert('RGB')

def generate_certificate_pdf(template_obj, candidate):
    from django.conf import settings

    # Convert template PDF to image
    pages = convert_from_path(template_obj.file.path, dpi=300)
    template_img = pages[0]

    # Save image to memory
    img_io = BytesIO()
    template_img.save(img_io, format='PNG')
    img_io.seek(0)
    background = ImageReader(img_io)

    # Create PDF buffer
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    c.drawImage(background, 0, 0, width=width, height=height)

    try:
        logo_path = candidate.company.logo.path  
        c.drawImage(logo_path, 40, height - 100, width=100, height=60, preserveAspectRatio=True, mask='auto')
    except:
        pass  

    for field in template_obj.fields.all():
        field_name = field.field_name.strip().lower().replace(" ", "_")

        if field_name == "company_name":
            value = candidate.company.company_name
        else:
            value = getattr(candidate, field_name, "")

        c.setFont(field.font, field.font_size)

        text_width = c.stringWidth(str(value), field.font, field.font_size)
        centered_x = (width - text_width) / 2

        c.drawString(centered_x, field.position_y, str(value))
   
    uid = str(uuid.uuid4())
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, f"Certificate ID: {uid}")

    qr = qrcode.make(f"http://127.0.0.1:8000/generateCertificate/verify/?id={uid}")
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)
    c.drawImage(ImageReader(qr_io), width - 150, 50, width=100, height=100)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return uid, pdf_buffer

