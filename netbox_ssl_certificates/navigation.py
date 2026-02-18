from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="SSL Certificates",
    icon_class="mdi mdi-certificate",
    groups=(
        (
            "",
            (
                PluginMenuItem(
                    link="plugins:netbox_ssl_certificates:certificate_dashboard",
                    link_text="Dashboard",
                ),
            ),
        ),
        (
            "Certificates",
            (
                PluginMenuItem(
                    link="plugins:netbox_ssl_certificates:certificate_list",
                    link_text="Certificates",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_ssl_certificates:certificate_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                        PluginMenuButton(
                            link="plugins:netbox_ssl_certificates:certificate_import",
                            title="Import",
                            icon_class="mdi mdi-upload",
                        ),
                        PluginMenuButton(
                            link="plugins:netbox_ssl_certificates:certificate_scan",
                            title="Scan",
                            icon_class="mdi mdi-magnify",
                        ),
                    ),
                ),
            ),
        ),
    ),
)