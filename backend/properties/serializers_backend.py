from rest_framework import serializers

from core.money import format_aed
from properties.models import Property


class PropertyListSerializer(serializers.ModelSerializer):
    current_rent = serializers.SerializerMethodField()
    market_rent = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            "id",
            "unit_ref",
            "type_label",
            "property_type",
            "area",
            "status",
            "bedrooms",
            "occupancy_status",
            "current_rent",
            "market_rent",
            "is_assumed",
        )

    def get_type_label(self, obj):
        return obj.type_label

    def get_current_rent(self, obj):
        if hasattr(obj, "rentdata"):
            return format_aed(obj.rentdata.current_annual_fils, obj.is_assumed)
        return ""

    def get_market_rent(self, obj):
        if hasattr(obj, "rentdata"):
            return format_aed(obj.rentdata.market_annual_fils, obj.is_assumed)
        return ""


class PropertyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            "id",
            "unit_ref",
            "property_type",
            "area",
            "bedrooms",
            "floor_area_sqm",
            "estimated_value_fils",
            "valuation_date",
            "valuation_source",
            "status",
            "occupancy_status",
            "vacancy_start_date",
            "target_occupancy_date",
            "photo_url",
            "notes",
            "is_assumed",
        )
        read_only_fields = ("id",)

    def validate_property_type(self, value):
        valid = {choice[0] for choice in Property.TYPE_CHOICES}
        if value not in valid:
            raise serializers.ValidationError("Invalid property type.")
        return value

    def validate_status(self, value):
        valid = {
            Property.STATUS_ACTIVE,
            Property.STATUS_INACTIVE,
            Property.STATUS_RENOVATION,
        }
        if value not in valid:
            raise serializers.ValidationError("Invalid property status.")
        return value

    def validate_occupancy_status(self, value):
        valid = {
            Property.OCCUPIED,
            Property.OCCUPANT_VACANT,
            Property.OCCUPANT_RENOVATION,
            Property.OCCUPANT_RESERVED,
        }
        if value not in valid:
            raise serializers.ValidationError("Invalid occupancy status.")
        return value

    def validate(self, attrs):
        for field in ("floor_area_sqm", "estimated_value_fils"):
            value = attrs.get(field)
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "Value cannot be negative."})
        if attrs.get("occupancy_status") == Property.OCCUPANT_VACANT and not attrs.get(
            "vacancy_start_date"
        ):
            instance = getattr(self, "instance", None)
            if not instance or not instance.vacancy_start_date:
                raise serializers.ValidationError(
                    {"vacancy_start_date": "Vacancy start date is required for vacant units."}
                )
        return attrs
