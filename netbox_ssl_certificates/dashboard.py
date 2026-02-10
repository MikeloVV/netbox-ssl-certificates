from django.db.models import Q, Count, Case, When, IntegerField
from django.urls import reverse
from netbox.plugins import PluginTemplateExtension
from .models import Certificate


class CertificateStatsWidget(PluginTemplateExtension):
    """Dashboard widget showing certificate statistics"""
    
    model = 'dcim.site'  # Привязываем к главной странице
    
    def get_context_data(self, request, instance):
        """Get certificate statistics"""
        
        # Общая статистика
        total = Certificate.objects.count()
        expired = Certificate.objects.filter(is_expired=True).count()
        expiring_soon = Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__lte=30,
            days_until_expiry__gte=0
        ).count()
        valid = Certificate.objects.filter(
            is_expired=False
        ).exclude(
            days_until_expiry__lte=30
        ).count()
        
        # Ближайшие к истечению
        expiring_certificates = Certificate.objects.filter(
            is_expired=False,
            days_until_expiry__gte=0
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