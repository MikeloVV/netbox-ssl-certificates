from django.core.management.base import BaseCommand
from netbox_ssl_certificates.scanner import auto_import_from_domain, scan_domain


class Command(BaseCommand):
    help = 'Scan domain and import SSL certificate'

    def add_arguments(self, parser):
        parser.add_argument(
            'hostname',
            type=str,
            help='Domain to scan (e.g., example.com)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=443,
            help='Port (default: 443)'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Certificate name (default: hostname:port)'
        )
        parser.add_argument(
            '--no-import',
            action='store_true',
            help='Only scan without importing'
        )
        parser.add_argument(
            '--no-update',
            action='store_true',
            help='Do not update existing certificates'
        )

    def handle(self, *args, **options):
        hostname = options['hostname']
        port = options['port']
        name = options.get('name')
        no_import = options['no_import']
        no_update = options['no_update']
        
        self.stdout.write(f'Scanning {hostname}:{port}...')
        
        if no_import:
            # Only scan
            result = scan_domain(hostname, port)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ Successfully scanned {hostname}:{port}')
                )
                self.stdout.write(f"  Protocol: {result.get('protocol', 'N/A')}")
                self.stdout.write(f"  Cipher: {result.get('cipher', ['N/A'])[0]}")
                self.stdout.write(f"\n  Certificate preview:")
                cert_lines = result['certificate'].split('\n')
                for line in cert_lines[:5]:
                    self.stdout.write(f"    {line}")
                self.stdout.write(f"    ... ({len(cert_lines)} total lines)")
            else:
                self.stdout.write(
                    self.style.ERROR(f'\n✗ Scan failed: {result["error"]}')
                )
        else:
            # Import certificate
            cert, message = auto_import_from_domain(
                hostname,
                port,
                name,
                update_existing=not no_update
            )
            
            if cert:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✓ {message}')
                )
                self.stdout.write(f'\nCertificate Details:')
                self.stdout.write(f'  Name: {cert.name}')
                self.stdout.write(f'  Common Name: {cert.common_name}')
                self.stdout.write(f'  Issuer: {cert.issuer}')
                self.stdout.write(f'  Valid From: {cert.valid_from}')
                self.stdout.write(f'  Valid Until: {cert.valid_until}')
                self.stdout.write(f'  Days Until Expiry: {cert.days_until_expiry}')
                self.stdout.write(f'  Status: {cert.status}')
                
                if cert.subject_alternative_names:
                    self.stdout.write(f'\n  SANs:')
                    for san in cert.subject_alternative_names[:5]:
                        self.stdout.write(f'    - {san}')
                    if len(cert.subject_alternative_names) > 5:
                        self.stdout.write(f'    ... and {len(cert.subject_alternative_names) - 5} more')
            else:
                self.stdout.write(
                    self.style.ERROR(f'\n✗ Import failed: {message}')
                )