from netbox.plugins import PluginTemplateExtension


class DeviceCertificates(PluginTemplateExtension):
    """Display certificates on device page"""
    
    model = 'dcim.device'
    
    def right_page(self):
        """Add certificates panel to device page"""
        obj = self.context['object']
        certificates = obj.certificates.all()
        
        if not certificates:
            return ''
        
        return self.render('netbox_ssl_certificates/inc/device_certificates.html', extra_context={
            'certificates': certificates,
            'object_type': 'Device',
        })


class VirtualMachineCertificates(PluginTemplateExtension):
    """Display certificates on virtual machine page"""
    
    model = 'virtualization.virtualmachine'
    
    def right_page(self):
        """Add certificates panel to VM page"""
        obj = self.context['object']
        certificates = obj.certificates.all()
        
        if not certificates:
            return ''
        
        return self.render('netbox_ssl_certificates/inc/device_certificates.html', extra_context={
            'certificates': certificates,
            'object_type': 'Virtual Machine',
        })


class SiteCertificates(PluginTemplateExtension):
    """Display certificates on site page"""
    
    model = 'dcim.site'
    
    def right_page(self):
        """Add certificates panel to site page"""
        obj = self.context['object']
        certificates = obj.certificates.all()
        
        if not certificates:
            return ''
        
        return self.render('netbox_ssl_certificates/inc/device_certificates.html', extra_context={
            'certificates': certificates,
            'object_type': 'Site',
        })

template_extensions = [DeviceCertificates, VirtualMachineCertificates, SiteCertificates]