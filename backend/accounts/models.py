from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    PORTAL_CHOICES = [
        ("client", "Client Dashboard"),
        ("backend", "Backend Portal"),
        ("both", "Both"),
    ]
    ROLE_CHOICES = [
        ("portfolio_owner", "Portfolio Owner"),
        ("system_admin", "System Admin"),
        ("property_manager", "Property Manager"),
        ("financial_analyst", "Financial Analyst"),
        ("viewer", "Viewer / Auditor"),
    ]

    portal = models.CharField(max_length=16, choices=PORTAL_CHOICES, default="backend")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="viewer")
    department = models.CharField(max_length=128, blank=True)
    is_active_account = models.BooleanField(default=True)

    @property
    def roles(self):
        return [self.role]
