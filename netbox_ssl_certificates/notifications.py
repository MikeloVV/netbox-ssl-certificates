from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Certificate
import logging

logger = logging.getLogger('netbox.plugins.netbox_ssl_certificates')


def send_expiry_notification(certificates, days_threshold=30):
    """Send email notification about expiring certificates"""
    
    if not certificates:
        logger.info("No certificates to notify about")
        return False
    
    # Get recipient list from plugin config
    plugin_config = settings.PLUGINS_CONFIG.get('netbox_ssl_certificates', {})
    recipient_list = plugin_config.get('notification_emails', [])
    
    if not recipient_list:
        logger.warning("No notification emails configured")
        return False
    
    subject = f'⚠️ SSL Certificates Expiring Soon ({len(certificates)} certificates)'
    
    context = {
        'certificates': certificates,
        'days_threshold': days_threshold,
        'netbox_url': settings.BASE_URL,
        'total_count': len(certificates),
    }
    
    # Render HTML email
    html_content = render_to_string(
        'netbox_ssl_certificates/email/expiry_notification.html',
        context
    )
    
    # Create plain text version
    text_content = strip_tags(html_content)
    
    try:
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Expiry notification sent to {', '.join(recipient_list)}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return False


def get_expiring_certificates(days=30):
    """Get certificates expiring within specified days"""
    return Certificate.objects.filter(
        is_expired=False,
        days_until_expiry__lte=days,
        days_until_expiry__gte=0
    ).order_by('valid_until')


def get_expired_certificates():
    """Get expired certificates"""
    return Certificate.objects.filter(is_expired=True).order_by('-valid_until')