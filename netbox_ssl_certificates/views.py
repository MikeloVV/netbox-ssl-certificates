from netbox.views import generic
from django.db.models import Q, Count, Case, When, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, FormView, View
from django.http import HttpResponse
from . import filtersets, forms, models, tables
from .scanner import auto_import_from_domain, scan_domain
import zipfile
import io


class CertificateDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view with certificate statistics and charts"""

    template_name = 'netbox_ssl_certificates/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Общая статистика
        total = models.Certificate.objects.count()
        expired = models.Certificate.objects.filter(is_expired=True).count()

        # ИСПРАВЛЕНО: Правильный фильтр для expiring_soon
        expiring_soon = models.Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__lte=30,
            days_until_expiry__gte=0
        ).count()

        valid = models.Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__gt=30  # ИСПРАВЛЕНО: больше 30 дней
        ).count()

        # Статистика по срокам истечения
        expiring_7_days = models.Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__lte=7,
            days_until_expiry__gte=0
        ).count()

        expiring_30_days = models.Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__lte=30,
            days_until_expiry__gt=7
        ).count()

        expiring_90_days = models.Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__lte=90,
            days_until_expiry__gt=30
        ).count()

        # Self-signed сертификаты
        self_signed = models.Certificate.objects.filter(is_self_signed=True).count()

        # Chain verified
        chain_verified = models.Certificate.objects.filter(
            chain_verified=True
        ).exclude(
            ca_certificate__isnull=True
        ).count()

        # ИСПРАВЛЕНО: Списки сертификатов с правильными фильтрами
        expiring_certificates = models.Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__lte=30,  # ИСПРАВЛЕНО: только до 30 дней
            days_until_expiry__gte=0
        ).order_by('valid_until')[:10]

        recently_expired = models.Certificate.objects.filter(
            is_expired=True
        ).order_by('-valid_until')[:10]

        recently_added = models.Certificate.objects.order_by('-created')[:10]

        context.update({
            'total': total,
            'expired': expired,
            'expiring_soon': expiring_soon,
            'valid': valid,
            'expiring_7_days': expiring_7_days,
            'expiring_30_days': expiring_30_days,
            'expiring_90_days': expiring_90_days,
            'self_signed': self_signed,
            'chain_verified': chain_verified,
            'expiring_certificates': expiring_certificates,
            'recently_expired': recently_expired,
            'recently_added': recently_added,
        })

        return context


class CertificateListView(generic.ObjectListView):
    queryset = models.Certificate.objects.all()
    table = tables.CertificateTable
    filterset = filtersets.CertificateFilterSet
    filterset_form = forms.CertificateFilterForm
    
    def get_extra_context(self, request):
        """Add statistics to context"""
        # Используйте self.filterset.qs вместо self.queryset для учета фильтров
        queryset = self.filterset.qs if hasattr(self, 'filterset') else self.queryset
        
        stats = {
            'total': queryset.count(),
            'valid': queryset.filter(
                is_expired=False,
                days_until_expiry__gt=30
            ).count(),
            'expiring_soon': queryset.filter(
                is_expired=False,
                days_until_expiry__lte=30,
                days_until_expiry__gte=0
            ).count(),
            'expired': queryset.filter(is_expired=True).count(),
        }
        
        return {'stats': stats}


class CertificateView(generic.ObjectView):
    queryset = models.Certificate.objects.all()


class CertificateEditView(generic.ObjectEditView):
    queryset = models.Certificate.objects.all()
    form = forms.CertificateForm


class CertificateDeleteView(generic.ObjectDeleteView):
    queryset = models.Certificate.objects.all()


class CertificateBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Certificate.objects.all()
    table = tables.CertificateTable


class CertificateImportView(LoginRequiredMixin, FormView):
    """View for importing certificates from files"""
    
    template_name = 'netbox_ssl_certificates/certificate_import.html'
    form_class = forms.CertificateImportForm
    
    def form_valid(self, form):
        try:
            # Create certificate
            certificate = models.Certificate(
                name=form.cleaned_data['name'],
                description=form.cleaned_data.get('description', ''),
                certificate_file=form.cleaned_data['certificate_file'],
                private_key=form.cleaned_data.get('private_key_file', ''),
            )
            
            # Handle CA certificate
            ca_cert_content = form.cleaned_data.get('ca_certificate_file')
            if ca_cert_content:
                # Create or find CA certificate
                ca_cert_name = f"CA-{form.cleaned_data['name']}"
                ca_cert, created = models.Certificate.objects.get_or_create(
                    name=ca_cert_name,
                    defaults={
                        'certificate_file': ca_cert_content,
                        'description': f'CA certificate for {form.cleaned_data["name"]}'
                    }
                )
                certificate.ca_certificate = ca_cert
            
            certificate.save()
            
            # Assign to devices/VMs/sites
            if form.cleaned_data.get('devices'):
                certificate.devices.set(form.cleaned_data['devices'])
            if form.cleaned_data.get('virtual_machines'):
                certificate.virtual_machines.set(form.cleaned_data['virtual_machines'])
            if form.cleaned_data.get('sites'):
                certificate.sites.set(form.cleaned_data['sites'])
            
            # Verify chain if requested
            if form.cleaned_data.get('verify_chain') and certificate.ca_certificate:
                verified, message = certificate.verify_chain()
                if verified:
                    messages.success(
                        self.request,
                        f'Certificate chain verified: {message}'
                    )
                else:
                    messages.warning(
                        self.request,
                        f'Certificate chain verification failed: {message}'
                    )
            
            messages.success(
                self.request,
                f'Certificate "{certificate.name}" imported successfully'
            )
            
            return redirect('plugins:netbox_ssl_certificates:certificate', pk=certificate.pk)
        
        except Exception as e:
            messages.error(
                self.request,
                f'Failed to import certificate: {str(e)}'
            )
            return self.form_invalid(form)


class CertificateScanView(LoginRequiredMixin, FormView):
    """View for scanning domains and importing certificates"""
    
    template_name = 'netbox_ssl_certificates/certificate_scan.html'
    form_class = forms.CertificateScanForm
    
    def form_valid(self, form):
        hostname = form.cleaned_data['hostname']
        port = form.cleaned_data['port']
        name = form.cleaned_data.get('name')
        update_existing = form.cleaned_data['update_existing']
        device = form.cleaned_data.get('assign_to_device')
        
        try:
            # Scan and import
            certificate, message = auto_import_from_domain(
                hostname,
                port,
                name,
                update_existing
            )
            
            if certificate:
                # Assign to device if specified
                if device:
                    certificate.devices.add(device)
                    certificate.save()
                
                messages.success(
                    self.request,
                    f'{message}: {certificate.name}'
                )
                
                return redirect('plugins:netbox_ssl_certificates:certificate', pk=certificate.pk)
            else:
                messages.error(
                    self.request,
                    f'Scan failed: {message}'
                )
                return self.form_invalid(form)
        
        except Exception as e:
            messages.error(
                self.request,
                f'Scan failed: {str(e)}'
            )
            return self.form_invalid(form)


class CertificateExportView(LoginRequiredMixin, View):
    """Export certificate and private key as ZIP"""
    
    def get(self, request, pk):
        certificate = get_object_or_404(models.Certificate, pk=pk)
        
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add certificate
            zip_file.writestr(
                f'{certificate.name}.crt',
                certificate.certificate_file
            )
            
            # Add private key if exists
            if certificate.private_key:
                zip_file.writestr(
                    f'{certificate.name}.key',
                    certificate.private_key
                )
            
            # Add CA certificate if exists
            if certificate.ca_certificate:
                zip_file.writestr(
                    f'{certificate.name}_ca.crt',
                    certificate.ca_certificate.certificate_file
                )
            
            # Add metadata
            metadata = f"""Certificate Information
======================

Name: {certificate.name}
Common Name: {certificate.common_name}
Issuer: {certificate.issuer}
Serial Number: {certificate.serial_number}

Validity:
---------
Valid From: {certificate.valid_from}
Valid Until: {certificate.valid_until}
Days Until Expiry: {certificate.days_until_expiry}
Status: {certificate.status}

Technical Details:
------------------
Key Size: {certificate.key_size} bits
Algorithm: {certificate.algorithm}
Self-Signed: {certificate.is_self_signed}
Fingerprint (SHA-256): {certificate.fingerprint_sha256}

Chain Verification:
-------------------
Chain Verified: {certificate.chain_verified}
Verification Message: {certificate.chain_verification_message}

Subject Alternative Names:
--------------------------
"""
            if certificate.subject_alternative_names:
                for san in certificate.subject_alternative_names:
                    metadata += f"- {san}\n"
            else:
                metadata += "None\n"
            
            metadata += f"\nAssigned Objects:\n-----------------\n"
            metadata += f"Devices: {certificate.devices.count()}\n"
            metadata += f"Virtual Machines: {certificate.virtual_machines.count()}\n"
            metadata += f"Sites: {certificate.sites.count()}\n"
            
            if certificate.description:
                metadata += f"\nDescription:\n------------\n{certificate.description}\n"
            
            if certificate.comments:
                metadata += f"\nComments:\n---------\n{certificate.comments}\n"
            
            zip_file.writestr(
                f'{certificate.name}_info.txt',
                metadata
            )
        
        # Prepare response
        response = HttpResponse(
            zip_buffer.getvalue(),
            content_type='application/zip'
        )
        response['Content-Disposition'] = f'attachment; filename="{certificate.name}.zip"'
        
        return response


class CertificateVerifyChainView(LoginRequiredMixin, View):
    """Verify certificate chain"""
    
    def post(self, request, pk):
        certificate = get_object_or_404(models.Certificate, pk=pk)
        
        if not certificate.ca_certificate:
            messages.warning(
                request,
                'No CA certificate specified for chain verification'
            )
        else:
            verified, message = certificate.verify_chain()
            
            if verified:
                messages.success(request, f'✓ {message}')
            else:
                messages.error(request, f'✗ {message}')
        
        return redirect('plugins:netbox_ssl_certificates:certificate', pk=pk)