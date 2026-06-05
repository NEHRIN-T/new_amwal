from django.db import models

from core.models import TimeStampedModel


class ManagementFeeConfig(TimeStampedModel):
    FEE_PERCENT = "percent"
    FEE_FIXED = "fixed"
    FEE_CHOICES = [(FEE_PERCENT, "Percentage"), (FEE_FIXED, "Fixed per unit")]

    fee_type = models.CharField(max_length=16, choices=FEE_CHOICES, default=FEE_PERCENT)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.8)
    fixed_fee_fils = models.BigIntegerField(default=0)
    effective_from = models.DateField()
    is_assumed = models.BooleanField(default=True)


class ScenarioConfig(TimeStampedModel):
    SCENARIO_BEAR = "bear"
    SCENARIO_BASE = "base"
    SCENARIO_BULL = "bull"
    SCENARIO_CHOICES = [
        (SCENARIO_BEAR, "Bear"),
        (SCENARIO_BASE, "Base"),
        (SCENARIO_BULL, "Bull"),
    ]

    scenario = models.CharField(max_length=16, choices=SCENARIO_CHOICES, unique=True)
    occupancy_pct = models.DecimalField(max_digits=5, decimal_places=2)
    rent_correction_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    growth_rate_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_assumed = models.BooleanField(default=True)


class ScenarioYearProjection(TimeStampedModel):
    scenario = models.ForeignKey(
        ScenarioConfig, on_delete=models.CASCADE, related_name="projections"
    )
    year_index = models.IntegerField()
    revenue_fils = models.BigIntegerField(default=0)
    is_assumed = models.BooleanField(default=True)

    class Meta:
        unique_together = ("scenario", "year_index")


class MonthlyRevenueSnapshot(TimeStampedModel):
    SCENARIO_CURRENT = "current"
    SCENARIO_POTENTIAL = "potential"
    SCENARIO_BEAR = "bear"
    SCENARIO_CHOICES = [
        (SCENARIO_CURRENT, "Current"),
        (SCENARIO_POTENTIAL, "Potential"),
        (SCENARIO_BEAR, "Bear"),
    ]

    year = models.IntegerField()
    month = models.IntegerField()
    scenario = models.CharField(max_length=16, choices=SCENARIO_CHOICES)
    amount_fils = models.BigIntegerField(default=0)
    is_assumed = models.BooleanField(default=True)

    class Meta:
        unique_together = ("year", "month", "scenario")
