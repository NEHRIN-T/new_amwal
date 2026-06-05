from django.db import models

from core.models import TimeStampedModel
from properties.models import Property
from core.gap import gap_status_from_fils


class RentData(TimeStampedModel):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="rentdata")
    current_annual_fils = models.BigIntegerField(default=0)
    current_monthly_fils = models.BigIntegerField(default=0)
    market_annual_fils = models.BigIntegerField(default=0)
    market_monthly_fils = models.BigIntegerField(default=0)
    dld_evidence_ref = models.TextField(blank=True)
    last_review_date = models.DateField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    is_assumed = models.BooleanField(default=True)
    annual_gap_fils = models.BigIntegerField(default=0)
    gap_status = models.CharField(max_length=16, default="at_market")

    def recalculate(self):
        self.annual_gap_fils = max(
            0, (self.market_annual_fils or 0) - (self.current_annual_fils or 0)
        )
        self.gap_status = gap_status_from_fils(self.annual_gap_fils)
        if self.market_annual_fils and not self.market_monthly_fils:
            self.market_monthly_fils = self.market_annual_fils // 12
        if self.current_annual_fils and not self.current_monthly_fils:
            self.current_monthly_fils = self.current_annual_fils // 12

    def save(self, *args, **kwargs):
        self.recalculate()
        super().save(*args, **kwargs)
