from rest_framework.routers import DefaultRouter

from rents.views import RentDataViewSet

router = DefaultRouter()
router.register("rent-data", RentDataViewSet, basename="rentdata")

urlpatterns = router.urls
