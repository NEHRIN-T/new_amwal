from rest_framework import viewsets

from core.models import AuditLog
from core.permissions import IsBackendUser, PropertyManagerRole
from tenants.models import Lease, Tenant
from tenants.serializers import LeaseSerializer, TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsBackendUser, PropertyManagerRole]


class LeaseViewSet(viewsets.ModelViewSet):
    queryset = Lease.objects.select_related("tenant", "linked_property")
    serializer_class = LeaseSerializer
    permission_classes = [IsBackendUser, PropertyManagerRole]

    def perform_create(self, serializer):
        lease = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action="create",
            entity_type="lease",
            entity_id=str(lease.id),
            message="Unit %s occupied - %s" % (lease.linked_property.unit_ref, lease.tenant.name),
        )

    def perform_update(self, serializer):
        lease = serializer.save()
        if lease.status in (Lease.STATUS_EXPIRED, Lease.STATUS_TERMINATED):
            AuditLog.objects.create(
                user=self.request.user,
                action="vacate",
                entity_type="lease",
                entity_id=str(lease.id),
                message="Unit %s vacated" % lease.linked_property.unit_ref,
            )
