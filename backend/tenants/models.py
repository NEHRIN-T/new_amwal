from django.conf import settings
from django.db import models

from core.encryption import decrypt_value, encrypt_value
from core.models import TimeStampedModel
from properties.models import Property


class Tenant(TimeStampedModel):
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=64, blank=True)
    email = models.EmailField(blank=True)
    emirates_id_encrypted = models.TextField(blank=True)
    nationality = models.CharField(max_length=64, blank=True)
    linked_property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, blank=True, related_name="tenants"
    )

    @property
    def emirates_id(self):
        return decrypt_value(self.emirates_id_encrypted)

    @emirates_id.setter
    def emirates_id(self, value):
        self.emirates_id_encrypted = encrypt_value(value or "")


class Lease(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"
    STATUS_TERMINATED = "terminated"
    STATUS_NOTICE = "notice_period"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_TERMINATED, "Terminated"),
        (STATUS_NOTICE, "Notice Period"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="leases")
    linked_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="leases")
    start_date = models.DateField()
    end_date = models.DateField()
    annual_rent_fils = models.BigIntegerField(default=0)
    monthly_rent_fils = models.BigIntegerField(default=0)
    payment_frequency = models.CharField(max_length=32, default="monthly")
    deposit_fils = models.BigIntegerField(default=0)
    status = models.CharField(max_length=32, default=STATUS_ACTIVE)
    contract_file = models.FileField(upload_to="leases/", blank=True, null=True)
    vacate_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_assumed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.annual_rent_fils and not self.monthly_rent_fils:
            self.monthly_rent_fils = self.annual_rent_fils // 12
        super().save(*args, **kwargs)
        self._sync_occupancy()

    def _sync_occupancy(self):
        prop = self.linked_property
        if self.status == self.STATUS_ACTIVE:
            prop.occupancy_status = Property.OCCUPIED
            prop.vacancy_start_date = None
        elif self.status in (self.STATUS_EXPIRED, self.STATUS_TERMINATED):
            prop.occupancy_status = Property.OCCUPANT_VACANT
            if self.vacate_date:
                prop.vacancy_start_date = self.vacate_date
            elif not prop.vacancy_start_date:
                from datetime import date

                prop.vacancy_start_date = date.today()
        prop.save(update_fields=["occupancy_status", "vacancy_start_date", "updated_at"])


class ActivityLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    message = models.TextField()
