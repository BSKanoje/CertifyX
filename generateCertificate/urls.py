from django.urls import path
from . import views

urlpatterns = [
    path('generate-certificate/', views.generate_certificates, name='generate_certificates'),
    path('verify/', views.verify_certificate, name='verify_certificate'),
    path('certificates/', views.certificate_list, name='certificate_list'),
]
