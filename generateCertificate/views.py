# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CertificateTemplate, Certificate, Candidate
from subscriptions.models import CompanySubscription
from .utils import generate_certificate_pdf
from django.core.files.base import ContentFile
from django.contrib import messages
from datetime import date

@login_required
def generate_certificates(request):
    if request.method == 'POST':
        template_id = request.POST.get('template')
        candidate_ids = request.POST.getlist('candidates')

        if not template_id or not candidate_ids:
            messages.error(request, 'Template and candidates must be selected.')
            return redirect('generate_certificates')

        try:
            template = CertificateTemplate.objects.get(id=template_id, company=request.user)
        except CertificateTemplate.DoesNotExist:
            messages.error(request, 'Invalid template selection.')
            return redirect('generate_certificates')

        candidates = Candidate.objects.filter(id__in=candidate_ids, company=request.user)

        try:
            subscription = CompanySubscription.objects.get(company=request.user)
        except CompanySubscription.DoesNotExist:
            messages.error(request, "No active subscription found.")
            return redirect('home')

        if not subscription.is_subscription_active():
            messages.error(request, "Your subscription has expired.")
            return redirect('home')

        if subscription.get_certificates_used() + len(candidates) > subscription.plan.certificate_limit:
            messages.error(
                request,
                f"You can only generate {subscription.remaining_certificates()} more certificates under your plan."
            )
            return redirect('generate_certificates')

        for candidate in candidates:
            uid, pdf_buffer = generate_certificate_pdf(template, candidate)
            pdf_buffer.seek(0)

            Certificate.objects.create(
                candidate=candidate,
                template=template,
                company=request.user,
                unique_id=uid,
                pdf_file=ContentFile(pdf_buffer.read(), name=f"{uid}.pdf"),
            )

        messages.success(request, 'Certificates generated successfully!')
        return redirect('certificate_list')

    else:
        templates = CertificateTemplate.objects.filter(company=request.user)
        candidates = Candidate.objects.filter(company=request.user)
        return render(request, 'generateCertificate/generate.html', {
            'templates': templates,
            'candidates': candidates
        })


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
