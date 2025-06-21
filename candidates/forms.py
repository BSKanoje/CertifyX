from django import forms
from .models import Candidate

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = '__all__'
        exclude = ['company']

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select an Excel file (.xlsx)')