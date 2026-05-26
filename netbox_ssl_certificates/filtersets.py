from datetime import timedelta
from django.db import models
from django.utils import timezone
import django_filters

from netbox.filtersets import NetBoxModelFilterSet
from .models import Certificate


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
    
    # Динамический фильтр «истёк / не истёк» через valid_until
    is_expired = django_filters.BooleanFilter(
        method='filter_is_expired',
        label='Is Expired'
    )
    
    class Meta:
        model = Certificate
        # ⚠️ убрали 'is_expired' из fields, т.к. это property,
        # и теперь обрабатывается кастомным методом filter_is_expired
        fields = ['id', 'name', 'common_name', 'issuer', 'is_self_signed']
    
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
    
    def filter_is_expired(self, queryset, name, value):
        """Filter by expiration status using valid_until field"""
        now = timezone.now()
        if value is True:
            return queryset.filter(valid_until__lt=now)
        elif value is False:
            return queryset.filter(valid_until__gte=now)
        return queryset
    
    def filter_status(self, queryset, name, value):
        """Filter by certificate status — dynamically via valid_until"""
        now = timezone.now()
        threshold_30d = now + timedelta(days=30)
        
        if value == 'expired':
            # valid_until < now
            return queryset.filter(valid_until__lt=now)
        elif value == 'expiring_soon':
            # now <= valid_until <= now + 30 days
            return queryset.filter(
                valid_until__gte=now,
                valid_until__lte=threshold_30d
            )
        elif value == 'valid':
            # valid_until > now + 30 days
            return queryset.filter(valid_until__gt=threshold_30d)
        
        return queryset