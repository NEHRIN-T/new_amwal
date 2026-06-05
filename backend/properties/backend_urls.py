from django.urls import path
from rest_framework.routers import DefaultRouter

from properties.backend_views import PropertyViewSet

router = DefaultRouter()
router.register("properties", PropertyViewSet, basename="property")

urlpatterns = router.urls
