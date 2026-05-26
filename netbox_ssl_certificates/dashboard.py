from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from netbox.plugins import PluginTemplateExtension
from .models import Certificate


class CertificateStatsWidget(PluginTemplateExtension):
    """Dashboard widget showing certificate statistics"""
    
    model = 'dcim.site'  # Привязываем к главной странице
    
    def get_context_data(self, request, instance):
        """Get certificate statistics"""
        
        now = timezone.now()
        soon = now + timedelta(days=30)
        
        # Общая статистика
        total = Certificate.objects.count()
        expired = Certificate.objects.filter(valid_until__lt=now).count()
        expiring_soon = Certificate.objects.filter(
            valid_until__gte=now,
            valid_until__lte=soon,
        ).count()
        valid = Certificate.objects.filter(valid_until__gt=soon).count()
        
        # Ближайшие к истечению (не истёкшие)
        expiring_certificates = Certificate.objects.filter(
            valid_until__gte=now,
        ).order_by('valid_until')[:5]
        
        return {
            'total': total,
            'expired': expired,
            'expiring_soon': expiring_soon,
            'valid': valid,
            'expiring_certificates': expiring_certificates,
            'certificate_list_url': reverse('plugins:netbox_ssl_certificates:certificate_list'),
        }


template_extensions = [CertificateStatsWidget]