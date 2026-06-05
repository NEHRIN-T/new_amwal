from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "severity", "property", "action_label", "is_dismissed")
    list_filter = ("severity", "category", "is_dismissed")
    search_fields = ("title", "category", "property__unit_ref")
    autocomplete_fields = ("property",)
