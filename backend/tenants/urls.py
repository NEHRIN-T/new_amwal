from rest_framework.routers import DefaultRouter

from tenants.views import LeaseViewSet, TenantViewSet

router = DefaultRouter()
router.register("tenants", TenantViewSet, basename="tenant")
router.register("leases", LeaseViewSet, basename="lease")

urlpatterns = router.urls
