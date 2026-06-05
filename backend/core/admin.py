from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "entity_type", "entity_id")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("action", "entity_type", "entity_id", "message", "user__username")
    readonly_fields = ("created_at", "updated_at", "user", "action", "entity_type", "entity_id", "message", "metadata")
