from django.contrib import admin

from .models import ActivityLog, Lease, Tenant


class LeaseInline(admin.TabularInline):
    model = Lease
    extra = 0
    fields = (
        "linked_property",
        "start_date",
        "end_date",
        "annual_rent_fils",
        "monthly_rent_fils",
        "payment_frequency",
        "status",
    )
    autocomplete_fields = ("linked_property",)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Tenant Record",
            {
                "fields": (
                    "name",
                    "contact_number",
                    "email",
                    "emirates_id_encrypted",
                    "nationality",
                    "linked_property",
                )
            },
        ),
    )
    list_display = ("name", "contact_number", "email", "nationality", "linked_property")
    list_filter = ("nationality",)
    search_fields = ("name", "contact_number", "email", "nationality", "linked_property__unit_ref")
    autocomplete_fields = ("linked_property",)
    inlines = (LeaseInline,)


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Lease Record",
            {
                "fields": (
                    "tenant",
                    "linked_property",
                    "start_date",
                    "end_date",
                    "annual_rent_fils",
                    "monthly_rent_fils",
                    "payment_frequency",
                    "deposit_fils",
                    "status",
                    "contract_file",
                    "vacate_date",
                    "notes",
                    "is_assumed",
                )
            },
        ),
    )
    list_display = (
        "tenant",
        "linked_property",
        "start_date",
        "end_date",
        "annual_rent_fils",
        "payment_frequency",
        "status",
    )
    list_filter = ("status", "payment_frequency", "is_assumed")
    search_fields = ("tenant__name", "linked_property__unit_ref", "notes")
    autocomplete_fields = ("tenant", "linked_property")
    date_hierarchy = "end_date"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "message")
    list_filter = ("created_at",)
    search_fields = ("message", "user__username")
    readonly_fields = ("created_at", "updated_at")
