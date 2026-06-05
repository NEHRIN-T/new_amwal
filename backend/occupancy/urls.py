from django.urls import path
from rest_framework.routers import DefaultRouter

from occupancy.views import OccupancyDashboardView, OccupancyUpdateView

router = DefaultRouter()

urlpatterns = [
    path("occupancy/dashboard/", OccupancyDashboardView.as_view()),
    path("occupancy/<int:pk>/status/", OccupancyUpdateView.as_view()),
]
