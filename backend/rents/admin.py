from django.contrib import admin

from .models import RentData


@admin.register(RentData)
class RentDataAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Rent & Market Data",
            {
                "fields": (
                    "property",
                    "current_annual_fils",
                    "current_monthly_fils",
                    "market_annual_fils",
                    "market_monthly_fils",
                    "dld_evidence_ref",
                    "last_review_date",
                    "review_notes",
                    "is_assumed",
                )
            },
        ),
        (
            "Calculated Gap",
            {
                "fields": (
                    "annual_gap_fils",
                    "gap_status",
                )
            },
        ),
    )
    list_display = (
        "property",
        "current_annual_fils",
        "market_annual_fils",
        "annual_gap_fils",
        "gap_status",
        "last_review_date",
    )
    list_filter = ("gap_status", "last_review_date", "is_assumed")
    search_fields = ("property__unit_ref", "property__area", "dld_evidence_ref", "review_notes")
    autocomplete_fields = ("property",)
    readonly_fields = ("annual_gap_fils", "gap_status")
    date_hierarchy = "last_review_date"
