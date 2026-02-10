from netbox.plugins import PluginConfig

class SSLCertificatesConfig(PluginConfig):
    name = 'netbox_ssl_certificates'
    verbose_name = 'SSL Certificates'
    description = 'Manage SSL certificates and track expiration dates'
    version = '1.0.4'
    author = 'Mikhail Voronov'
    author_email = 'mikhail.voronov@gmail.com'
    base_url = 'ssl-certificates'
    min_version = '4.0.0'
    max_version = '4.9.99'
    required_settings = []
    default_settings = {
        'expiry_warning_days': 30,
        'enable_notifications': True,
        'notification_emails': [],
    }
# Регистрация homepage panels
#    def ready(self):
#        super().ready()
#        from . import homepage
#        # Регистрируем панели
#        from netbox.plugins import register_homepage_panels
#        register_homepage_panels(homepage.panels)

#def ready(self):
#        super().ready()
#        
#        # Register template extensions
#        from . import template_content
        
config = SSLCertificatesConfig