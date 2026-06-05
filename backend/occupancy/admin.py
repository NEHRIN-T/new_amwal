from django.contrib import admin

from .models import MonthlyOccupancySnapshot, OccupancyHistory


@admin.register(OccupancyHistory)
class OccupancyHistoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Occupancy Management",
            {
                "fields": (
                    "property",
                    "status",
                    "effective_date",
                    "reason",
                    "notes",
                    "changed_by",
                )
            },
        ),
    )
    list_display = ("property", "status", "effective_date", "reason", "changed_by")
    list_filter = ("status", "reason", "effective_date")
    search_fields = ("property__unit_ref", "property__area", "reason", "notes", "changed_by__username")
    autocomplete_fields = ("property", "changed_by")
    date_hierarchy = "effective_date"


@admin.register(MonthlyOccupancySnapshot)
class MonthlyOccupancySnapshotAdmin(admin.ModelAdmin):
    list_display = ("year", "month", "occupied_count", "vacant_count", "income_fils", "is_assumed")
    list_filter = ("year", "month", "is_assumed")
    ordering = ("year", "month")
