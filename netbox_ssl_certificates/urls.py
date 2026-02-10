from django.urls import path
from netbox.views.generic import ObjectChangeLogView
from . import views
from .models import Certificate

urlpatterns = [
    # Dashboard
    path('', views.CertificateDashboardView.as_view(), name='certificate_dashboard'),
    
    # Certificate CRUD
    path('certificates/', views.CertificateListView.as_view(), name='certificate_list'),
    path('certificates/add/', views.CertificateEditView.as_view(), name='certificate_add'),
    path('certificates/<int:pk>/', views.CertificateView.as_view(), name='certificate'),
    path('certificates/<int:pk>/edit/', views.CertificateEditView.as_view(), name='certificate_edit'),
    path('certificates/<int:pk>/delete/', views.CertificateDeleteView.as_view(), name='certificate_delete'),
    path('certificates/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='certificate_changelog', kwargs={'model': Certificate}),
    path('certificates/delete/', views.CertificateBulkDeleteView.as_view(), name='certificate_bulk_delete'),
    
    # Import & Export
    path('import/', views.CertificateImportView.as_view(), name='certificate_import'),
    path('certificates/<int:pk>/export/', views.CertificateExportView.as_view(), name='certificate_export'),
    
    # Scan
    path('scan/', views.CertificateScanView.as_view(), name='certificate_scan'),
    
    # Chain verification
    path('certificates/<int:pk>/verify-chain/', views.CertificateVerifyChainView.as_view(), name='certificate_verify_chain'),
]