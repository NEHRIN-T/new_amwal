from rest_framework import viewsets

from core.permissions import IsBackendUser, PropertyManagerRole
from properties.models import Property
from properties.serializers_backend import PropertyListSerializer, PropertyWriteSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().select_related("rentdata")
    permission_classes = [IsBackendUser, PropertyManagerRole]
    search_fields = ["unit_ref", "area"]
    filterset_fields = ["property_type", "area", "occupancy_status", "status"]
    ordering_fields = [
        "unit_ref",
        "property_type",
        "area",
        "status",
        "bedrooms",
        "occupancy_status",
    ]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PropertyListSerializer
        return PropertyWriteSerializer
