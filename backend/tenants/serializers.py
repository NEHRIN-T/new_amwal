from rest_framework import serializers

from tenants.models import Lease, Tenant


class TenantSerializer(serializers.ModelSerializer):
    emirates_id = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Tenant
        fields = "__all__"
        extra_kwargs = {"emirates_id_encrypted": {"read_only": True}}

    def create(self, validated_data):
        eid = validated_data.pop("emirates_id", "")
        tenant = Tenant(**validated_data)
        tenant.emirates_id = eid
        tenant.save()
        return tenant

    def update(self, instance, validated_data):
        eid = validated_data.pop("emirates_id", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if eid is not None:
            instance.emirates_id = eid
        instance.save()
        return instance

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Tenant name is required.")
        return value


class LeaseSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    unit_ref = serializers.CharField(source="linked_property.unit_ref", read_only=True)

    class Meta:
        model = Lease
        fields = "__all__"

    def validate_status(self, value):
        valid = {choice[0] for choice in Lease.STATUS_CHOICES}
        if value not in valid:
            raise serializers.ValidationError("Invalid lease status.")
        return value

    def validate_payment_frequency(self, value):
        valid = {"monthly", "quarterly", "annual", "2_cheques", "4_cheques"}
        if value not in valid:
            raise serializers.ValidationError("Invalid payment frequency.")
        return value

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        status = attrs.get("status", getattr(self.instance, "status", None))
        vacate_date = attrs.get("vacate_date", getattr(self.instance, "vacate_date", None))
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "Lease end date must be after start date."})
        for field in ("annual_rent_fils", "monthly_rent_fils", "deposit_fils"):
            value = attrs.get(field)
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "Value cannot be negative."})
        if attrs.get("annual_rent_fils") == 0:
            raise serializers.ValidationError({"annual_rent_fils": "Annual rent must be greater than zero."})
        if status in (Lease.STATUS_EXPIRED, Lease.STATUS_TERMINATED) and not vacate_date:
            raise serializers.ValidationError(
                {"vacate_date": "Vacate date is required when ending a lease."}
            )
        return attrs
