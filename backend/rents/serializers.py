from rest_framework import serializers

from core.money import format_aed
from rents.models import RentData


class RentGapRowSerializer(serializers.ModelSerializer):
    unit_ref = serializers.CharField(source="property.unit_ref")
    type_label = serializers.CharField(source="property.type_label")
    area = serializers.CharField(source="property.area")
    market_rent = serializers.SerializerMethodField()
    current_rent = serializers.SerializerMethodField()
    gap_yr = serializers.SerializerMethodField()
    last_review = serializers.DateField(source="last_review_date")
    status = serializers.CharField(source="gap_status")

    class Meta:
        model = RentData
        fields = (
            "unit_ref",
            "type_label",
            "area",
            "market_rent",
            "current_rent",
            "gap_yr",
            "last_review",
            "status",
            "is_assumed",
        )

    def get_market_rent(self, obj):
        return format_aed(obj.market_annual_fils, obj.is_assumed)

    def get_current_rent(self, obj):
        return format_aed(obj.current_annual_fils, obj.is_assumed)

    def get_gap_yr(self, obj):
        return format_aed(obj.annual_gap_fils, obj.is_assumed)


class RentDataSerializer(serializers.ModelSerializer):
    unit_ref = serializers.CharField(source="property.unit_ref", read_only=True)

    class Meta:
        model = RentData
        fields = "__all__"
        read_only_fields = ("annual_gap_fils", "gap_status")

    def validate(self, attrs):
        for field in (
            "current_annual_fils",
            "current_monthly_fils",
            "market_annual_fils",
            "market_monthly_fils",
        ):
            value = attrs.get(field)
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "Value cannot be negative."})
        if attrs.get("current_annual_fils") == 0:
            raise serializers.ValidationError(
                {"current_annual_fils": "Current annual rent must be greater than zero."}
            )
        if attrs.get("market_annual_fils") == 0:
            raise serializers.ValidationError(
                {"market_annual_fils": "Market annual rent must be greater than zero."}
            )
        return attrs
