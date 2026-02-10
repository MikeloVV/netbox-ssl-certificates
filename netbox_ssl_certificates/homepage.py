from netbox.plugins import PluginHomePagePanel
from django.db.models import Q
from .models import Certificate


class CertificateStatsPanel(PluginHomePagePanel):
    """Homepage panel for certificate statistics"""
    
    template_name = 'netbox_ssl_certificates/inc/homepage_panel.html'
    
    def get_context_data(self, request):
        """Get certificate statistics"""
        
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
        
        # Недавно истекшие
        recently_expired = Certificate.objects.filter(
            is_expired=True
        ).order_by('-valid_until')[:5]
        
        return {
            'total': total,
            'expired': expired,
            'expiring_soon': expiring_soon,
            'valid': valid,
            'expiring_certificates': expiring_certificates,
            'recently_expired': recently_expired,
        }


panels = [CertificateStatsPanel]