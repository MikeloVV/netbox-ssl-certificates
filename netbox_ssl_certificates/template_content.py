from netbox.plugins import PluginTemplateExtension


class ObjectCertificates(PluginTemplateExtension):
    """Display certificates on device, VM and site pages"""
    
    # Один класс для всех типов объектов
    model = ['dcim.device', 'virtualization.virtualmachine', 'dcim.site']
    
    def right_page(self):
        """Add certificates panel to object page"""
        obj = self.context.get('object')
        
        if not obj or not hasattr(obj, 'certificates'):
            return ''
        
        certificates = obj.certificates.all()
        
        if not certificates.exists():
            return ''
        
        # Определяем тип объекта для заголовка
        object_type = obj._meta.verbose_name.title()
        
        return self.render(
            'netbox_ssl_certificates/inc/device_certificates.html',
            extra_context={
                'certificates': certificates,
                'object_type': object_type,
            }
        )


template_extensions = [ObjectCertificates]