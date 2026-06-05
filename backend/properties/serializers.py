from rest_framework import serializers

from core.money import format_aed
from properties.models import Property
from properties.services import days_vacant


class PropertyCardSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()

    def get_type_label(self, obj):
        return obj.type_label
    rent_month = serializers.SerializerMethodField()
    gap_year = serializers.SerializerMethodField()
    gap_below_market = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            "id",
            "unit_ref",
            "type_label",
            "property_type",
            "area",
            "occupancy_status",
            "status_label",
            "photo_url",
            "rent_month",
            "gap_year",
            "gap_below_market",
            "is_assumed",
        )

    def get_status_label(self, obj):
        return "Occupied" if obj.occupancy_status == Property.OCCUPIED else "Vacant"

    def get_rent_month(self, obj):
        if hasattr(obj, "rentdata"):
            return format_aed(obj.rentdata.current_monthly_fils or 0, obj.is_assumed)
        return ""

    def get_gap_year(self, obj):
        if hasattr(obj, "rentdata") and obj.rentdata.annual_gap_fils > 0:
            return format_aed(obj.rentdata.annual_gap_fils, obj.is_assumed)
        return None

    def get_gap_below_market(self, obj):
        return hasattr(obj, "rentdata") and obj.rentdata.annual_gap_fils > 0
