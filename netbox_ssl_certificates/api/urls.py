from netbox.api.routers import NetBoxRouter
from .views import CertificateViewSet

app_name = 'netbox_ssl_certificates-api'

router = NetBoxRouter()
router.register('certificates', CertificateViewSet)

urlpatterns = router.urls