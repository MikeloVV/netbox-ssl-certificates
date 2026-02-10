from django.core.management.base import BaseCommand
from netbox_ssl_certificates.notifications import (
    get_expiring_certificates,
    send_expiry_notification
)


class Command(BaseCommand):
    help = 'Send email notifications about expiring certificates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days threshold for expiry warning (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        certificates = get_expiring_certificates(days)
        
        if certificates:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {certificates.count()} certificate(s) expiring within {days} days:'
                )
            )
            
            for cert in certificates:
                status = '🔴' if cert.days_until_expiry <= 7 else '🟡'
                self.stdout.write(
                    f'  {status} {cert.name} - expires in {cert.days_until_expiry} days '
                    f'({cert.valid_until.strftime("%Y-%m-%d")})'
                )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('\n[DRY RUN] No emails sent')
                )
            else:
                success = send_expiry_notification(list(certificates), days)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('\n✓ Notification sent successfully')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('\n✗ Failed to send notification')
                    )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ No certificates expiring within {days} days')
            )