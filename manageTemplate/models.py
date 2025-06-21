from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from pdf2image import convert_from_path
from PIL import Image
import os, uuid

FONT_CHOICES = [
    ('Times New Roman', 'Times New Roman'),
    ('Helvetica', 'Helvetica'),
    ('Courier New', 'Courier New'),
]

class CertificateTemplate(models.Model):
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    file = models.FileField(
                upload_to='certificate_templates/',
                validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
                null=True,
                blank=True,
            )
    preview_image = models.ImageField(upload_to='previews/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the PDF first

        # Convert PDF to PNG for preview
        if self.file and self.file.name.endswith('.pdf'):
            preview_path = self.convert_pdf_to_png()
            if preview_path:
                self.preview_image.name = preview_path
                super().save(update_fields=['preview_image'])

    def convert_pdf_to_png(self):
        POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"
        try:
            print("Converting PDF to PNG:", self.file.path)
            pages = convert_from_path(self.file.path, dpi=150, poppler_path=POPPLER_PATH)

            from django.conf import settings
            output_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
            os.makedirs(output_dir, exist_ok=True)

            filename = f'{uuid.uuid4()}.png'
            output_path = os.path.join(output_dir, filename)
            pages[0].save(output_path, 'PNG')

            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            print("Saved preview at:", relative_path)
            return relative_path.replace('\\', '/')
        except Exception as e:
            print("PDF to PNG conversion error:", e)
            return None

    def __str__(self):
        return f"{self.name} - {self.company.company_name}"


class DynamicField(models.Model):
    template = models.ForeignKey(CertificateTemplate, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100)  
    font = models.CharField(choices=FONT_CHOICES, max_length=50, default='Helvetica')
    font_size = models.PositiveIntegerField(default=12)
    position_x = models.PositiveIntegerField() 
    position_y = models.PositiveIntegerField() 

    def __str__(self):
        return f"{self.field_name} on {self.template.name}"



