from django.urls import path

from properties.client_views import (
    FinancialDashboardView,
    OccupancyView,
    PortfolioOverviewView,
    PropertyListView,
    RentalIntelligenceView,
)

urlpatterns = [
    path("portfolio/", PortfolioOverviewView.as_view()),
    path("properties/", PropertyListView.as_view()),
    path("rental-intelligence/", RentalIntelligenceView.as_view()),
    path("occupancy/", OccupancyView.as_view()),
    path("financial/", FinancialDashboardView.as_view()),
]
