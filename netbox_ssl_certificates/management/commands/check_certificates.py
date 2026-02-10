from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
from netbox_ssl_certificates.models import Certificate
from datetime import datetime, timezone


class Command(BaseCommand):
    help = 'Check SSL certificates expiration and send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Warn about certificates expiring within this many days'
        )

    def handle(self, *args, **options):
        warning_days = options['days']
        now = datetime.now(timezone.utc)
        
        # Обновляем статус всех сертификатов
        for cert in Certificate.objects.all():
            cert.save()  # Это пересчитает все поля
        
        # Находим сертификаты, которые истекают
        expiring_certs = Certificate.objects.filter(
            days_until_expiry__lte=warning_days,
            days_until_expiry__gte=0
        )
        
        expired_certs = Certificate.objects.filter(is_expired=True)
        
        if expiring_certs.exists() or expired_certs.exists():
            self.send_notification(expiring_certs, expired_certs)
            self.stdout.write(
                self.style.WARNING(
                    f'Found {expiring_certs.count()} expiring and {expired_certs.count()} expired certificates'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('All certificates are valid'))

    def send_notification(self, expiring_certs, expired_certs):
        """Send email notification about expiring certificates"""
        
        message_parts = []
        
        if expired_certs.exists():
            message_parts.append("EXPIRED CERTIFICATES:\n")
            for cert in expired_certs:
                message_parts.append(
                    f"- {cert.name} (CN: {cert.common_name}) - "
                    f"expired {abs(cert.days_until_expiry)} days ago\n"
                )
        
        if expiring_certs.exists():
            message_parts.append("\nEXPIRING SOON:\n")
            for cert in expiring_certs:
                message_parts.append(
                    f"- {cert.name} (CN: {cert.common_name}) - "
                    f"expires in {cert.days_until_expiry} days\n"
                )
        
        message = ''.join(message_parts)
        
        # Отправка email (требует настройки SMTP в NetBox)
        try:
            send_mail(
                subject='SSL Certificate Expiration Warning',
                message=message,
                from_email=settings.EMAIL_FROM,
                recipient_list=[settings.ADMINS[0][1]] if settings.ADMINS else [],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Notification sent successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send notification: {str(e)}'))