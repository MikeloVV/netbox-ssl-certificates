import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import Certificate


class CertificateTable(NetBoxTable):
    """Table for displaying certificates"""
    
    name = tables.Column(
        linkify=True
    )
    
    common_name = tables.Column(
        verbose_name='Common Name'
    )
    
    issuer = tables.Column(
        verbose_name='Issuer'
    )
    
    valid_until = tables.DateTimeColumn(
        format='Y-m-d H:i',
        verbose_name='Valid Until'
    )
    
    # ⚠️ Теперь это @property, поэтому:
    #    - accessor явно указывает на property
    #    - orderable=False (сортировать по property через ORM нельзя)
    #    - order_by='valid_until' позволяет всё равно сортировать колонку,
    #      используя поле БД valid_until (эквивалентно по смыслу)
    days_until_expiry = tables.Column(
        accessor='days_until_expiry',
        verbose_name='Days Until Expiry',
        order_by='valid_until',
        attrs={'td': {'class': 'text-end'}}
    )
    
    # status тоже @property — указываем accessor и используем order_by='valid_until'
    status = tables.TemplateColumn(
        template_code='''
        {% if record.status == 'expired' %}
            <span class="badge bg-danger">Expired</span>
        {% elif record.status == 'expiring_soon' %}
            <span class="badge bg-warning">Expiring Soon</span>
        {% else %}
            <span class="badge bg-success">Valid</span>
        {% endif %}
        ''',
        verbose_name='Status',
        order_by='valid_until'
    )
    
    class Meta(NetBoxTable.Meta):
        model = Certificate
        fields = (
            'pk', 'id', 'name', 'common_name', 'issuer', 'valid_from', 
            'valid_until', 'days_until_expiry', 'status', 'created', 'last_updated'
        )
        default_columns = (
            'name', 'common_name', 'issuer', 'valid_until', 'days_until_expiry', 'status'
        )