from netbox.api.viewsets import NetBoxModelViewSet
from netbox_ssl_certificates.models import Certificate
from netbox_ssl_certificates.filtersets import CertificateFilterSet
from .serializers import CertificateSerializer


class CertificateViewSet(NetBoxModelViewSet):
    """REST API viewset for Certificate model"""
    
    queryset = Certificate.objects.prefetch_related('tags')
    serializer_class = CertificateSerializer
    filterset_class = CertificateFilterSet