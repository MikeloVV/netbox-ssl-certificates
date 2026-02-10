from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from netbox.models import NetBoxModel
from dcim.models import Device, Site
from virtualization.models import VirtualMachine
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from datetime import datetime, timezone


def validate_certificate_matches_key(certificate_file, private_key):
    """Validate that private key matches certificate"""
    if not private_key:
        return True
    
    try:
        # Load certificate
        cert = x509.load_pem_x509_certificate(
            certificate_file.encode('utf-8'),
            default_backend()
        )
        
        # Load private key
        key = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # Compare public keys
        cert_public_key = cert.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        key_public_key = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        if cert_public_key != key_public_key:
            raise ValidationError('Private key does not match certificate')
        
        return True
    
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Validation error: {str(e)}')


class Certificate(NetBoxModel):
    """Model for SSL/TLS certificates"""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Unique name for the certificate'
    )
    description = models.TextField(
        blank=True,
        help_text='Description of the certificate'
    )
    certificate_file = models.TextField(
        help_text='PEM encoded certificate content'
    )
    private_key = models.TextField(
        blank=True,
        help_text='PEM encoded private key (optional)'
    )
    
    # CA Certificate for chain verification
    ca_certificate = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_certificates',
        help_text='CA certificate for chain verification'
    )
    
    # Связи с объектами NetBox
    devices = models.ManyToManyField(
        to='dcim.Device',
        related_name='certificates',
        blank=True,
        help_text='Devices using this certificate'
    )
    virtual_machines = models.ManyToManyField(
        to='virtualization.VirtualMachine',
        related_name='certificates',
        blank=True,
        help_text='Virtual machines using this certificate'
    )
    sites = models.ManyToManyField(
        to='dcim.Site',
        related_name='certificates',
        blank=True,
        help_text='Sites using this certificate'
    )
    
    # Auto-populated fields from certificate
    common_name = models.CharField(
        max_length=255,
        blank=True,
        editable=False,
        db_index=True
    )
    subject_alternative_names = models.JSONField(
        default=list,
        blank=True,
        help_text='List of SANs'
    )
    issuer = models.CharField(max_length=255, blank=True, editable=False)
    serial_number = models.CharField(max_length=100, blank=True, editable=False)
    valid_from = models.DateTimeField(null=True, blank=True, editable=False)
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        db_index=True
    )
    fingerprint_sha256 = models.CharField(
        max_length=95,
        blank=True,
        editable=False,
        help_text='SHA-256 fingerprint'
    )
    is_self_signed = models.BooleanField(default=False, editable=False)
    key_size = models.IntegerField(null=True, blank=True, editable=False)
    algorithm = models.CharField(max_length=50, blank=True, editable=False)
    is_expired = models.BooleanField(
        default=False,
        editable=False,
        db_index=True
    )
    days_until_expiry = models.IntegerField(null=True, blank=True, editable=False)
    
    # Chain verification status
    chain_verified = models.BooleanField(
        default=False,
        editable=False,
        help_text='Certificate chain verification status'
    )
    chain_verification_message = models.TextField(
        blank=True,
        editable=False,
        help_text='Chain verification details'
    )
    
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'SSL Certificate'
        verbose_name_plural = 'SSL Certificates'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ssl_certificates:certificate', args=[self.pk])

    @property
    def status(self):
        """Return certificate status"""
        if self.is_expired:
            return 'expired'
        elif self.days_until_expiry is not None and self.days_until_expiry <= 30:
            return 'expiring_soon'
        return 'valid'

    @property
    def status_color(self):
        """Return color for status badge"""
        status_colors = {
            'valid': 'success',
            'expiring_soon': 'warning',
            'expired': 'danger',
        }
        return status_colors.get(self.status, 'secondary')
    
    @property
    def assigned_objects_count(self):
        """Return total count of assigned objects"""
        return (
            self.devices.count() +
            self.virtual_machines.count() +
            self.sites.count()
        )

    def clean(self):
        """Validate certificate and private key"""
        super().clean()
        
        if self.certificate_file and self.private_key:
            validate_certificate_matches_key(
                self.certificate_file,
                self.private_key
            )

    def save(self, *args, **kwargs):
        """Parse certificate on save"""
        if self.certificate_file:
            self._parse_certificate()
        
        # Verify chain if CA certificate is set
        if self.ca_certificate:
            self._verify_chain()
        
        super().save(*args, **kwargs)

    def _parse_certificate(self):
        """Parse certificate and extract metadata"""
        try:
            cert_bytes = self.certificate_file.encode('utf-8')
            cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
            
            # Extract common name
            try:
                self.common_name = cert.subject.get_attributes_for_oid(
                    x509.oid.NameOID.COMMON_NAME
                )[0].value
            except (IndexError, AttributeError):
                self.common_name = 'N/A'
            
            # Extract issuer
            try:
                self.issuer = cert.issuer.get_attributes_for_oid(
                    x509.oid.NameOID.COMMON_NAME
                )[0].value
            except (IndexError, AttributeError):
                self.issuer = 'N/A'
            
            # Extract SANs
            try:
                san_ext = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                self.subject_alternative_names = [
                    str(name.value) for name in san_ext.value
                ]
            except x509.ExtensionNotFound:
                self.subject_alternative_names = []
            
            # Serial number
            self.serial_number = format(cert.serial_number, 'X')
            
            # Validity dates
            self.valid_from = cert.not_valid_before_utc
            self.valid_until = cert.not_valid_after_utc
            
            # Calculate expiry
            now = datetime.now(timezone.utc)
            self.is_expired = now > self.valid_until
            self.days_until_expiry = (self.valid_until - now).days
            
            # Fingerprint
            fingerprint = cert.fingerprint(hashes.SHA256())
            self.fingerprint_sha256 = ':'.join(
                format(b, '02X') for b in fingerprint
            )
            
            # Check if self-signed
            self.is_self_signed = cert.issuer == cert.subject
            
            # Key size and algorithm
            public_key = cert.public_key()
            self.key_size = public_key.key_size
            self.algorithm = cert.signature_algorithm_oid._name
            
        except Exception as e:
            raise ValueError(f'Failed to parse certificate: {str(e)}')

    def _verify_chain(self):
        """Verify certificate chain with CA certificate"""
        if not self.ca_certificate:
            self.chain_verified = False
            self.chain_verification_message = "No CA certificate specified"
            return
        
        try:
            cert_bytes = self.certificate_file.encode('utf-8')
            cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
            
            ca_bytes = self.ca_certificate.certificate_file.encode('utf-8')
            ca_cert = x509.load_pem_x509_certificate(ca_bytes, default_backend())
            
            # Verify signature
            try:
                ca_public_key = ca_cert.public_key()
                ca_public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    cert.signature_hash_algorithm,
                )
                self.chain_verified = True
                self.chain_verification_message = "Certificate chain is valid"
            except InvalidSignature:
                self.chain_verified = False
                self.chain_verification_message = "Certificate signature verification failed"
            except Exception as e:
                self.chain_verified = False
                self.chain_verification_message = f"Verification error: {str(e)}"
        
        except Exception as e:
            self.chain_verified = False
            self.chain_verification_message = f"Chain verification error: {str(e)}"

    def verify_chain(self):
        """Public method to verify chain and save"""
        self._verify_chain()
        self.save()
        return self.chain_verified, self.chain_verification_message