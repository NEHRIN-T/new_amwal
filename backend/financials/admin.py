from django.contrib import admin

from .models import (
    ManagementFeeConfig,
    MonthlyRevenueSnapshot,
    ScenarioConfig,
    ScenarioYearProjection,
)


class ScenarioYearProjectionInline(admin.TabularInline):
    model = ScenarioYearProjection
    extra = 0
    fields = ("year_index", "revenue_fils", "is_assumed")


@admin.register(ManagementFeeConfig)
class ManagementFeeConfigAdmin(admin.ModelAdmin):
    list_display = ("fee_type", "fee_percentage", "fixed_fee_fils", "effective_from", "is_assumed")
    list_filter = ("fee_type", "effective_from", "is_assumed")
    date_hierarchy = "effective_from"


@admin.register(ScenarioConfig)
class ScenarioConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Scenario Model Configuration",
            {
                "fields": (
                    "scenario",
                    "occupancy_pct",
                    "rent_correction_pct",
                    "growth_rate_pct",
                    "description",
                    "is_assumed",
                )
            },
        ),
    )
    list_display = (
        "scenario",
        "occupancy_pct",
        "rent_correction_pct",
        "growth_rate_pct",
        "is_assumed",
    )
    list_filter = ("scenario", "is_assumed")
    search_fields = ("scenario", "description")
    inlines = (ScenarioYearProjectionInline,)


@admin.register(ScenarioYearProjection)
class ScenarioYearProjectionAdmin(admin.ModelAdmin):
    list_display = ("scenario", "year_index", "revenue_fils", "is_assumed")
    list_filter = ("scenario", "year_index", "is_assumed")
    autocomplete_fields = ("scenario",)


@admin.register(MonthlyRevenueSnapshot)
class MonthlyRevenueSnapshotAdmin(admin.ModelAdmin):
    list_display = ("year", "month", "scenario", "amount_fils", "is_assumed")
    list_filter = ("year", "month", "scenario", "is_assumed")
    ordering = ("year", "month", "scenario")
