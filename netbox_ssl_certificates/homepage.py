from datetime import timedelta
from django.utils import timezone
from netbox.plugins import PluginHomePagePanel
from .models import Certificate


class CertificateStatsPanel(PluginHomePagePanel):
    """Homepage panel for certificate statistics"""
    
    template_name = 'netbox_ssl_certificates/inc/homepage_panel.html'
    
    def get_context_data(self, request):
        """Get certificate statistics"""
        
        now = timezone.now()
        soon = now + timedelta(days=30)
        
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
        
        # Недавно истекшие
        recently_expired = Certificate.objects.filter(
            valid_until__lt=now,
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