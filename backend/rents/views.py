from datetime import date

from rest_framework import viewsets

from core.permissions import FinancialAnalystRole, IsBackendUser
from rents.models import RentData
from rents.serializers import RentDataSerializer


class RentDataViewSet(viewsets.ModelViewSet):
    queryset = RentData.objects.select_related("property")
    serializer_class = RentDataSerializer
    permission_classes = [IsBackendUser, FinancialAnalystRole]
    search_fields = ["property__unit_ref", "property__area"]
    ordering_fields = ["annual_gap_fils", "last_review_date"]

    def perform_update(self, serializer):
        instance = serializer.save(is_assumed=False, last_review_date=date.today())
        instance.recalculate()
        instance.save()
