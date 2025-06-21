from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('templates/upload/', views.upload_template, name='upload_template'),
    path('template/<int:template_id>/fields/', views.manage_fields, name='manage_fields'),

]
