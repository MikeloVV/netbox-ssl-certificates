from netbox.plugins import PluginMenuItem, PluginMenuButton

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_ssl_certificates:certificate_dashboard',
        link_text='Dashboard',
        permissions=['netbox_ssl_certificates.view_certificate'],
        buttons=()
    ),
    PluginMenuItem(
        link='plugins:netbox_ssl_certificates:certificate_list',
        link_text='Certificates',
        permissions=['netbox_ssl_certificates.view_certificate'],
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_ssl_certificates:certificate_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=['netbox_ssl_certificates.add_certificate']
            ),
            PluginMenuButton(
                link='plugins:netbox_ssl_certificates:certificate_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=['netbox_ssl_certificates.add_certificate']
            ),
            PluginMenuButton(
                link='plugins:netbox_ssl_certificates:certificate_scan',
                title='Scan Domain',
                icon_class='mdi mdi-radar',
                permissions=['netbox_ssl_certificates.add_certificate']
            ),
        )
    ),
)