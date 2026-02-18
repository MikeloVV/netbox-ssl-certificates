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
                    link="plugins:netbox_ssl_certificates:sslcertificate_list",
                    link_text="SSL Certificates",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:netbox_ssl_certificates:sslcertificate_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
    ),
)