import ssl
import socket
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from .models import Certificate
import logging

logger = logging.getLogger('netbox.plugins.netbox_ssl_certificates')


def scan_domain(hostname, port=443, timeout=10):
    """Scan domain and retrieve SSL certificate"""
    
    logger.info(f"Scanning {hostname}:{port}")
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get certificate in DER format
                der_cert = ssock.getpeercert(binary_form=True)
                
                # Convert to PEM
                cert = x509.load_der_x509_certificate(der_cert, default_backend())
                pem_cert = cert.public_bytes(
                    encoding=serialization.Encoding.PEM
                ).decode('utf-8')
                
                # Get certificate chain
                chain = []
                try:
                    # Try to get full chain (not always available)
                    chain_certs = ssock.get_peer_cert_chain()
                    if chain_certs:
                        for chain_cert in chain_certs[1:]:  # Skip first (server cert)
                            chain_pem = chain_cert.public_bytes(
                                encoding=serialization.Encoding.PEM
                            ).decode('utf-8')
                            chain.append(chain_pem)
                except AttributeError:
                    # get_peer_cert_chain not available in all Python versions
                    pass
                
                logger.info(f"Successfully scanned {hostname}:{port}")
                
                return {
                    'success': True,
                    'certificate': pem_cert,
                    'chain': chain,
                    'hostname': hostname,
                    'port': port,
                    'protocol': ssock.version(),
                    'cipher': ssock.cipher(),
                }
    
    except socket.timeout:
        error = f"Connection timeout after {timeout} seconds"
        logger.error(f"Scan failed for {hostname}:{port} - {error}")
        return {
            'success': False,
            'error': error,
            'hostname': hostname,
            'port': port,
        }
    except socket.gaierror as e:
        error = f"DNS resolution failed: {str(e)}"
        logger.error(f"Scan failed for {hostname}:{port} - {error}")
        return {
            'success': False,
            'error': error,
            'hostname': hostname,
            'port': port,
        }
    except ssl.SSLError as e:
        error = f"SSL error: {str(e)}"
        logger.error(f"Scan failed for {hostname}:{port} - {error}")
        return {
            'success': False,
            'error': error,
            'hostname': hostname,
            'port': port,
        }
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        logger.error(f"Scan failed for {hostname}:{port} - {error}")
        return {
            'success': False,
            'error': error,
            'hostname': hostname,
            'port': port,
        }


def auto_import_from_domain(hostname, port=443, name=None, update_existing=True):
    """Automatically import certificate from domain"""
    
    result = scan_domain(hostname, port)
    
    if not result['success']:
        return None, result['error']
    
    certificate_name = name or f"{hostname}:{port}"
    
    # Check if certificate already exists
    existing = Certificate.objects.filter(name=certificate_name).first()
    
    description = f"Auto-imported from {hostname}:{port}"
    if result.get('protocol'):
        description += f" (Protocol: {result['protocol']}, Cipher: {result['cipher'][0]})"
    
    if existing:
        if update_existing:
            # Update existing certificate
            existing.certificate_file = result['certificate']
            existing.description = description
            existing.save()
            logger.info(f"Updated certificate: {certificate_name}")
            return existing, "Certificate updated"
        else:
            return existing, "Certificate already exists (not updated)"
    else:
        # Create new certificate
        cert = Certificate(
            name=certificate_name,
            description=description,
            certificate_file=result['certificate'],
        )
        cert.save()
        logger.info(f"Created new certificate: {certificate_name}")
        return cert, "Certificate imported"


def bulk_scan_domains(hostnames, port=443):
    """Scan multiple domains"""
    results = []
    
    for hostname in hostnames:
        result = scan_domain(hostname.strip(), port)
        results.append(result)
    
    return results