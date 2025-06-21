from django import forms
from .models import CertificateTemplate, DynamicField

class CertificateTemplateForm(forms.ModelForm):
    class Meta:
        model = CertificateTemplate
        fields = ['name', 'file']

class DynamicFieldForm(forms.ModelForm):
    class Meta:
        model = DynamicField
        fields = ['field_name', 'font', 'font_size', 'position_x', 'position_y']
        widgets = {
            'field_name': forms.TextInput(attrs={'class': 'form-control'}),
            'font': forms.Select(attrs={'class': 'form-control'}),
            'font_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'position_x': forms.NumberInput(attrs={'class': 'form-control'}),
            'position_y': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TemplateForm(forms.ModelForm):
    class Meta:
        model = CertificateTemplate
        fields = ['name', 'file']
