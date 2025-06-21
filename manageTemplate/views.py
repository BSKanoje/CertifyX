from django.shortcuts import render, redirect, get_object_or_404
from .models import CertificateTemplate, DynamicField
from .forms import CertificateTemplateForm, DynamicFieldForm
from subscriptions.models import CompanySubscription
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def upload_template(request):
    subscription = get_object_or_404(CompanySubscription, company=request.user)

    if CertificateTemplate.objects.filter(company=request.user).count() >= subscription.plan.template_limit:
        messages.error(request, "You have reached your template upload limit for your current plan.")
        return redirect('template_list')

    if request.method == 'POST':
        form = CertificateTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.company = request.user
            template.save()
            messages.success(request, "Template uploaded successfully!")
            return redirect('template_list')
    else:
        form = CertificateTemplateForm()

    return render(request, 'manageTemplate/upload_template.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from .models import CertificateTemplate, DynamicField
from .forms import DynamicFieldForm

def manage_fields(request, template_id):
    template = get_object_or_404(CertificateTemplate, id=template_id)
    form = DynamicFieldForm(request.POST or None)
    fields = template.fields.all()

    image_url = template.preview_image.url if template.preview_image else "" 

    if request.method == 'POST' and form.is_valid():
        field_name = form.cleaned_data['field_name']
        
        existing = template.fields.filter(field_name=field_name).first()
        if existing:
            existing.font = form.cleaned_data['font']
            existing.font_size = form.cleaned_data['font_size']
            existing.position_x = form.cleaned_data['position_x']
            existing.position_y = form.cleaned_data['position_y']
            existing.save()
        else:
            new_field = form.save(commit=False)
            new_field.template = template
            new_field.save()

        return redirect('manage_fields', template_id=template.id)

    return render(request, 'manageTemplate/manage_fields.html', {
        'form': form,
        'fields': fields,
        'template': template,
        'image_url': image_url,
    })



from django.contrib import messages

def template_list(request):
    user = request.user
    subscription = user.subscription  
    templates = CertificateTemplate.objects.filter(company=user)
    template_count = templates.count()
    template_limit = subscription.plan.template_limit if subscription and subscription.plan else 0

    if request.method == 'POST':
        if template_count >= template_limit:
            messages.error(request, "Template upload limit reached. Upgrade your plan to upload more.")
            return redirect('template_list')

        form = CertificateTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.company = request.user
            template.save()
            messages.success(request, "Template uploaded successfully.")
            return redirect('template_list')
    else:
        form = CertificateTemplateForm()

    return render(request, 'manageTemplate/template_list.html', {
        'form': form, 
        'templates': templates, 
        'subscription': subscription,
        'template_limit': template_limit,
        'template_count': template_count,
        })








