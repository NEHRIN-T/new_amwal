from django.db import models

from core.models import TimeStampedModel
from properties.models import Property


class Alert(TimeStampedModel):
    SEVERITY_CRITICAL = "critical"
    SEVERITY_URGENT = "urgent"
    SEVERITY_REVIEW = "review"
    SEVERITY_WARNING = "warning"

    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=64)
    severity = models.CharField(max_length=32)
    action_label = models.CharField(max_length=32, default="View")
    is_dismissed = models.BooleanField(default=False)
