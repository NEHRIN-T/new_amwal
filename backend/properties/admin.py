from django.contrib import admin

from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Property Management",
            {
                "fields": (
                    "unit_ref",
                    "property_type",
                    "area",
                    "bedrooms",
                    "floor_area_sqm",
                    "estimated_value_fils",
                    "valuation_date",
                    "valuation_source",
                    "photo_url",
                    "notes",
                )
            },
        ),
        (
            "Status & Occupancy",
            {
                "fields": (
                    "status",
                    "occupancy_status",
                    "vacancy_start_date",
                    "target_occupancy_date",
                    "is_assumed",
                )
            },
        ),
    )
    list_display = (
        "unit_ref",
        "property_type",
        "area",
        "status",
        "occupancy_status",
        "bedrooms",
        "estimated_value_fils",
    )
    list_filter = ("property_type", "area", "status", "occupancy_status", "is_assumed")
    search_fields = ("unit_ref", "area", "notes")
    ordering = ("unit_ref",)
