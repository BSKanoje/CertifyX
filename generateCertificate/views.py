# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CertificateTemplate, Certificate, Candidate
from subscriptions.models import CompanySubscription
from .utils import generate_certificate_pdf
from django.core.files.base import ContentFile
from django.contrib import messages
from datetime import date

def verify_certificate(request):
    context = {}
    
    if request.method == 'POST':
        cert_id = request.POST.get('certificate_id')

        if cert_id:
            try:
                certificate = Certificate.objects.select_related('candidate', 'template', 'company').get(unique_id=cert_id)

                status = "Valid"

                context['certificate'] = {
                    'student_name': certificate.candidate.name,
                    'project_title': certificate.template.name,
                    'company_name': certificate.company.company_name,
                    'issue_date': certificate.issue_date.strftime('%B %d, %Y'),
                    'status': status
                }
            except Certificate.DoesNotExist:
                context['error'] = "Invalid Certificate ID."

    return render(request, 'generateCertificate/verify_certificate.html', context)


@login_required
def certificate_list(request):
    certificates = Certificate.objects.filter(
        candidate__company=request.user
    ).select_related('candidate', 'template')
    return render(request, 'generateCertificate/certificate_list.html', {'certificates': certificates})
