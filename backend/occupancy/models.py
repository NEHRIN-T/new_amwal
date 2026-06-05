from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from properties.models import Property


class OccupancyHistory(TimeStampedModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="occupancy_history")
    status = models.CharField(max_length=32)
    effective_date = models.DateField()
    reason = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )


class MonthlyOccupancySnapshot(TimeStampedModel):
    year = models.IntegerField()
    month = models.IntegerField()
    occupied_count = models.IntegerField(default=0)
    vacant_count = models.IntegerField(default=0)
    income_fils = models.BigIntegerField(default=0)
    is_assumed = models.BooleanField(default=True)

    class Meta:
        unique_together = ("year", "month")
        ordering = ["year", "month"]
