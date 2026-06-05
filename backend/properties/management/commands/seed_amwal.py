import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.money import aed_to_fils
from financials.models import (
    ManagementFeeConfig,
    MonthlyRevenueSnapshot,
    ScenarioConfig,
    ScenarioYearProjection,
)
from occupancy.models import MonthlyOccupancySnapshot
from properties.models import Property
from rents.models import RentData
from tenants.models import Lease, Tenant

User = get_user_model()

AREAS = {
    Property.TYPE_LX_VILLA: ["Palm Jumeirah", "Emirates Hills", "Al Barari", "JGE", "Sobha Hartland"],
    Property.TYPE_STD_VILLA: ["JGE", "Arabian Ranches", "Dubai Hills", "Al Barari"],
    Property.TYPE_LARGER_APT: ["Downtown", "Dubai Marina", "JLT", "Business Bay"],
    Property.TYPE_STD_FLAT: ["JVC", "Sports City", "Discovery Gardens", "International City"],
}

RENT_RANGES = {
    Property.TYPE_LX_VILLA: (280000, 520000),
    Property.TYPE_STD_VILLA: (140000, 220000),
    Property.TYPE_LARGER_APT: (85000, 140000),
    Property.TYPE_STD_FLAT: (45000, 75000),
}

VALUE_RANGES = {
    Property.TYPE_LX_VILLA: (6_000_000, 12_000_000),
    Property.TYPE_STD_VILLA: (2_500_000, 4_500_000),
    Property.TYPE_LARGER_APT: (1_000_000, 2_000_000),
    Property.TYPE_STD_FLAT: (550_000, 950_000),
}

PREFIX = {
    Property.TYPE_LX_VILLA: "LV",
    Property.TYPE_STD_VILLA: "SV",
    Property.TYPE_LARGER_APT: "LA",
    Property.TYPE_STD_FLAT: "SF",
}

COUNTS = {
    Property.TYPE_LX_VILLA: 8,
    Property.TYPE_STD_VILLA: 12,
    Property.TYPE_LARGER_APT: 20,
    Property.TYPE_STD_FLAT: 20,
}


class Command(BaseCommand):
    help = "Seed AMWAL demo data (60 properties, users, financials)"

    def handle(self, *args, **options):
        if Property.objects.exists():
            self.stdout.write("Data exists, skipping seed.")
            return
        random.seed(42)
        self._users()
        props = self._properties()
        self._rents(props)
        self._leases(props)
        self._snapshots()
        self._financials()
        self.stdout.write(self.style.SUCCESS("AMWAL seed complete."))

    def _users(self):
        users = [
            ("owner", "client", "portfolio_owner", "H. Siddiqui"),
            ("admin", "backend", "system_admin", "System Admin"),
            ("pmanager", "backend", "property_manager", "Property Manager"),
            ("analyst", "backend", "financial_analyst", "Financial Analyst"),
            ("viewer", "backend", "viewer", "Viewer Auditor"),
        ]
        for username, portal, role, name in users:
            u, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@amwal.ae"})
            if created:
                u.set_password("amwal123")
                u.first_name = name.split()[0]
                u.last_name = name.split()[-1] if len(name.split()) > 1 else ""
                u.portal = portal
                u.role = role
                u.save()

    def _properties(self):
        props = []
        photo_base = "https://images.unsplash.com/photo-1600596542815"
        for ptype, count in COUNTS.items():
            prefix = PREFIX[ptype]
            for i in range(1, count + 1):
                ref = f"{prefix}-{i:02d}"
                area = random.choice(AREAS[ptype])
                val = random.randint(*VALUE_RANGES[ptype])
                occ = Property.OCCUPIED if random.random() < 0.85 else Property.OCCUPANT_VACANT
                vac_date = None
                if occ == Property.OCCUPANT_VACANT:
                    vac_date = date.today() - timedelta(days=random.randint(15, 99))
                p = Property.objects.create(
                    unit_ref=ref,
                    property_type=ptype,
                    area=area,
                    bedrooms="4-5BR" if "Villa" in ptype else random.choice(["Studio/1BR", "2-3BR"]),
                    estimated_value_fils=aed_to_fils(val),
                    status=Property.STATUS_ACTIVE,
                    occupancy_status=occ,
                    vacancy_start_date=vac_date,
                    photo_url=f"{photo_base}-{i}?w=400&h=300&fit=crop",
                    is_assumed=True,
                )
                props.append(p)
        return props

    def _rents(self, props):
        for p in props:
            lo, hi = RENT_RANGES[p.property_type]
            market = random.randint(lo, hi)
            discount = random.uniform(0.72, 1.02)
            current = int(market * discount)
            RentData.objects.create(
                property=p,  # RentData FK
                current_annual_fils=aed_to_fils(current),
                current_monthly_fils=aed_to_fils(current) // 12,
                market_annual_fils=aed_to_fils(market),
                market_monthly_fils=aed_to_fils(market) // 12,
                last_review_date=date(2024, 7, 8),
                is_assumed=True,
            )

    def _leases(self, props):
        for p in props:
            if p.occupancy_status != Property.OCCUPIED:
                continue
            t = Tenant.objects.create(
                name="Tenant %s" % p.unit_ref,
                contact_number="+971500000000",
                email="tenant.%s@example.com" % p.unit_ref.lower(),
                nationality="UAE",
                linked_property=p,
            )
            t.emirates_id = "784-1990-0000000-%d" % random.randint(1, 9)
            t.save()
            rent = p.rentdata
            Lease.objects.create(
                tenant=t,
                linked_property=p,
                start_date=date(2023, 1, 1),
                end_date=date(2025, 12, 31),
                annual_rent_fils=rent.current_annual_fils,
                monthly_rent_fils=rent.current_monthly_fils,
                status=Lease.STATUS_ACTIVE,
                is_assumed=True,
            )

    def _snapshots(self):
        base_income = 33_000_00
        for m in range(1, 13):
            income = int(base_income * (0.9 + m * 0.05) + random.randint(-500000, 500000))
            occ = 51 if m % 3 else 50
            MonthlyOccupancySnapshot.objects.create(
                year=2025,
                month=m,
                occupied_count=occ,
                vacant_count=60 - occ,
                income_fils=income,
                is_assumed=True,
            )
            MonthlyRevenueSnapshot.objects.create(
                year=2025, month=m, scenario=MonthlyRevenueSnapshot.SCENARIO_CURRENT,
                amount_fils=int(income * 1.75), is_assumed=True,
            )
            MonthlyRevenueSnapshot.objects.create(
                year=2025, month=m, scenario=MonthlyRevenueSnapshot.SCENARIO_POTENTIAL,
                amount_fils=int(income * 2.4), is_assumed=True,
            )
            MonthlyRevenueSnapshot.objects.create(
                year=2025, month=m, scenario=MonthlyRevenueSnapshot.SCENARIO_BEAR,
                amount_fils=int(income * 1.4), is_assumed=True,
            )

    def _financials(self):
        ManagementFeeConfig.objects.create(
            fee_type="percent",
            fee_percentage=5.8,
            effective_from=date(2024, 1, 1),
            is_assumed=True,
        )
        scenarios = [
            ("bear", 78, 0, 0, "Bear - 78% occ., no rent fixes. ~AED 5.4M/yr", 5_400_000),
            ("base", 85, 15, 2, "Base - 85% occ., partial corrections. ~AED 7.0M/yr", 7_000_000),
            ("bull", 94, 100, 5, "Bull - 94% occ., market rents. ~AED 9.7M/yr", 9_700_000),
        ]
        for key, occ, rent, growth, desc, base in scenarios:
            cfg = ScenarioConfig.objects.create(
                scenario=key,
                occupancy_pct=occ,
                rent_correction_pct=rent,
                growth_rate_pct=growth,
                description=desc,
                is_assumed=True,
            )
            rev = aed_to_fils(base)
            for yr in range(1, 6):
                factor = 1 + (growth / 100) * (yr - 1)
                ScenarioYearProjection.objects.create(
                    scenario=cfg,
                    year_index=yr,
                    revenue_fils=int(rev * factor),
                    is_assumed=True,
                )
