from netbox.filtersets import NetBoxModelFilterSet
from .models import Certificate
from django.db import models
import django_filters


class CertificateFilterSet(NetBoxModelFilterSet):
    """FilterSet for certificates"""
    
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    
    status = django_filters.ChoiceFilter(
        method='filter_status',
        choices=[
            ('valid', 'Valid'),
            ('expiring_soon', 'Expiring Soon'),
            ('expired', 'Expired'),
        ],
        label='Status'
    )
    
    class Meta:
        model = Certificate
        fields = ['id', 'name', 'common_name', 'issuer', 'is_expired', 'is_self_signed']
    
    def search(self, queryset, name, value):
        """Custom search method"""
        if not value.strip():
            return queryset
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(common_name__icontains=value) |
            models.Q(issuer__icontains=value) |
            models.Q(description__icontains=value)
        )
    
    def filter_status(self, queryset, name, value):
        """Filter by certificate status"""
        from django.db.models import Q
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        if value == 'expired':
            return queryset.filter(is_expired=True)
        elif value == 'expiring_soon':
            return queryset.filter(
                is_expired=False,
                days_until_expiry__lte=30,
                days_until_expiry__gte=0
            )
        elif value == 'valid':
            return queryset.filter(
                is_expired=False
            ).exclude(
                days_until_expiry__lte=30
            )
        
        return queryset