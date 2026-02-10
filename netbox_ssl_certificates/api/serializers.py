from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from netbox_ssl_certificates.models import Certificate


class CertificateSerializer(NetBoxModelSerializer):
    """REST API serializer for Certificate model"""
    
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_ssl_certificates-api:certificate-detail'
    )
    
    display = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    status_color = serializers.CharField(read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'url', 'display', 'name', 'description', 'certificate_file', 
            'private_key', 'common_name', 'subject_alternative_names', 'issuer', 
            'serial_number', 'valid_from', 'valid_until', 'fingerprint_sha256', 
            'is_self_signed', 'key_size', 'algorithm', 'is_expired', 
            'days_until_expiry', 'status', 'status_color', 'comments',
            'created', 'last_updated', 'tags', 'custom_fields'
        ]
        read_only_fields = [
            'common_name', 'subject_alternative_names', 'issuer', 'serial_number',
            'valid_from', 'valid_until', 'fingerprint_sha256', 'is_self_signed',
            'key_size', 'algorithm', 'is_expired', 'days_until_expiry', 'status',
            'status_color', 'display'
        ]
        brief_fields = ['id', 'url', 'display', 'name', 'common_name']
    
    def get_display(self, obj):
        return str(obj)