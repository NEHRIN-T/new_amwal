from django.urls import path

from financials.views import (
    FeeConfigView,
    ScenarioConfigView,
    ValuationBulkView,
)

urlpatterns = [
    path("financial/fees/", FeeConfigView.as_view()),
    path("financial/scenarios/", ScenarioConfigView.as_view()),
    path("financial/valuations/", ValuationBulkView.as_view()),
]
