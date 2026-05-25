from netbox.filtersets import NetBoxModelFilterSet
from .models import Certificate
from django.db import models
from datetime import timedelta
from django.utils import timezone
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
    
    # Фильтр is_expired через метод (поскольку это property, а не поле БД)
    is_expired = django_filters.BooleanFilter(
        method='filter_is_expired',
        label='Is Expired'
    )
    
    class Meta:
        model = Certificate
        # ⚠️ Убрали 'is_expired' отсюда — он теперь объявлен явно выше
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
        """Filter by expiration based on valid_until field"""
        now = timezone.now()
        if value is True:
            return queryset.filter(valid_until__lt=now)
        elif value is False:
            return queryset.filter(valid_until__gte=now)
        return queryset
    
    def filter_status(self, queryset, name, value):
        """Filter by certificate status using valid_until field"""
        now = timezone.now()
        soon_threshold = now + timedelta(days=30)
        
        if value == 'expired':
            return queryset.filter(valid_until__lt=now)
        elif value == 'expiring_soon':
            return queryset.filter(
                valid_until__gte=now,
                valid_until__lte=soon_threshold
            )
        elif value == 'valid':
            return queryset.filter(valid_until__gt=soon_threshold)
        
        return queryset