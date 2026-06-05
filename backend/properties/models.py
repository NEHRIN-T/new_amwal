from django.db import models

from core.models import TimeStampedModel


class Property(TimeStampedModel):
    TYPE_LX_VILLA = "lx_villa"
    TYPE_STD_VILLA = "std_villa"
    TYPE_LARGER_APT = "larger_apt"
    TYPE_STD_FLAT = "std_flat"

    TYPE_CHOICES = [
        (TYPE_LX_VILLA, "Luxury Villa"),
        (TYPE_STD_VILLA, "Standard Villa"),
        (TYPE_LARGER_APT, "Larger Apartment"),
        (TYPE_STD_FLAT, "Standard Flat"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_RENOVATION = "renovation"

    OCCUPIED = "occupied"
    OCCUPANT_VACANT = "vacant"
    OCCUPANT_RENOVATION = "under_renovation"
    OCCUPANT_RESERVED = "reserved"

    unit_ref = models.CharField(max_length=32, unique=True)
    property_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    area = models.CharField(max_length=128)
    bedrooms = models.CharField(max_length=32, blank=True)
    floor_area_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_value_fils = models.BigIntegerField(default=0)
    valuation_date = models.DateField(null=True, blank=True)
    valuation_source = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, default=STATUS_ACTIVE)
    occupancy_status = models.CharField(max_length=32, default=OCCUPANT_VACANT)
    vacancy_start_date = models.DateField(null=True, blank=True)
    target_occupancy_date = models.DateField(null=True, blank=True)
    photo_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_assumed = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "properties"
        ordering = ["unit_ref"]

    def __str__(self):
        return self.unit_ref

    @property
    def type_label(self):
        return dict(self.TYPE_CHOICES).get(self.property_type, "")
