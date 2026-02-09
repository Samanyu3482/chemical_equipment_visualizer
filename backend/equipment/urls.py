from django.urls import path, include
from . import views

app_name = 'equipment'

urlpatterns = [
    # Equipment API endpoints
    path('upload/', views.upload_csv, name='upload_csv'),
    path('summary/', views.get_summary, name='get_summary'),
    path('history/', views.get_history, name='get_history'),
    path('report/pdf/', views.generate_pdf_report, name='generate_pdf_report'),
    path('sample-csv/', views.get_sample_csv, name='get_sample_csv'),
    
    # Authentication endpoints
    path('auth/', include('equipment.auth_urls')),
]