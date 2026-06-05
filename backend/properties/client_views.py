from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from core.money import format_aed
from core.permissions import IsClientReadOnly
from financials import services as fin
from occupancy.models import MonthlyOccupancySnapshot
from properties import services as svc
from properties.models import Property
from properties.serializers import PropertyCardSerializer
from rents.models import RentData
from rents.serializers import RentGapRowSerializer


class PortfolioOverviewView(APIView):
    permission_classes = [IsClientReadOnly]

    def get(self, request):
        counts = svc.portfolio_counts()
        assumed = True
        return Response(
            {
                "kpis": {
                    "total_units": counts["total"],
                    "total_breakdown": "8 LV - 12 Villas - 20 Apts - 20 Flats",
                    "occupancy_rate": svc.occupancy_rate(),
                    "occupied": counts["occupied"],
                    "vacant": counts["vacant"],
                    "monthly_income": format_aed(svc.monthly_income_fils(), assumed),
                    "monthly_income_fils": svc.monthly_income_fils(),
                    "rent_leakage_yr": format_aed(svc.rent_leakage_yearly_fils(), assumed),
                    "market_potential_yr": format_aed(svc.market_potential_yearly_fils(), assumed),
                    "is_assumed": assumed,
                },
                "composition": svc.composition_by_type(),
                "occupancy_by_category": svc.occupancy_by_category(),
                "income_trend": self._income_trend(),
            }
        )

    def _income_trend(self):
        snaps = MonthlyOccupancySnapshot.objects.order_by("year", "month")[:12]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return [
            {
                "month": months[s.month - 1],
                "income_fils": s.income_fils,
                "income_display": format_aed(s.income_fils, s.is_assumed),
            }
            for s in snaps
        ]


class PropertyListView(APIView):
    permission_classes = [IsClientReadOnly]

    def get(self, request):
        qs = Property.objects.filter(status=Property.STATUS_ACTIVE).select_related("rentdata")
        tab = request.query_params.get("tab", "all")
        search = request.query_params.get("search", "").strip()
        if tab == "lx_villas":
            qs = qs.filter(property_type=Property.TYPE_LX_VILLA)
        elif tab == "villas":
            qs = qs.filter(property_type=Property.TYPE_STD_VILLA)
        elif tab == "apartments":
            qs = qs.filter(property_type=Property.TYPE_LARGER_APT)
        elif tab == "flats":
            qs = qs.filter(property_type=Property.TYPE_STD_FLAT)
        elif tab == "vacant":
            qs = qs.filter(occupancy_status=Property.OCCUPANT_VACANT)
        if search:
            qs = qs.filter(Q(unit_ref__icontains=search) | Q(area__icontains=search))
        return Response(PropertyCardSerializer(qs, many=True).data)


class RentalIntelligenceView(APIView):
    permission_classes = [IsClientReadOnly]

    def get(self, request):
        kpis = svc.rental_intelligence_kpis()
        assumed = True
        return Response(
            {
                "kpis": {
                    "leakage_yr": format_aed(kpis["leakage_yearly_fils"], assumed),
                    "units_below_market": kpis["units_below_market"],
                    "units_below_pct": kpis["units_below_pct"],
                    "avg_gap_yr": format_aed(kpis["avg_gap_yearly_fils"], assumed),
                    "at_or_above_market": kpis["at_or_above_market"],
                    "at_or_above_pct": kpis["at_or_above_pct"],
                    "max_gap_yr": format_aed(kpis["max_gap_yearly_fils"], assumed),
                    "max_gap_unit_ref": kpis["max_gap_unit_ref"],
                },
                "gap_by_type": svc.gap_by_property_type(),
                "gap_distribution": svc.gap_distribution(),
                "units": RentGapRowSerializer(
                    RentData.objects.filter(property__status=Property.STATUS_ACTIVE)
                    .select_related("property")
                    .order_by("-annual_gap_fils"),
                    many=True,
                ).data,
            }
        )


class OccupancyView(APIView):
    permission_classes = [IsClientReadOnly]

    def get(self, request):
        counts = svc.portfolio_counts()
        critical = sum(
            1
            for p in Property.objects.filter(occupancy_status=Property.OCCUPANT_VACANT)
            if svc.days_vacant(p) > 60
        )
        max_days = 0
        max_ref = ""
        vacant_rows = []
        for p in Property.objects.filter(
            occupancy_status=Property.OCCUPANT_VACANT, status=Property.STATUS_ACTIVE
        ).select_related("rentdata"):
            days = svc.days_vacant(p)
            if days > max_days:
                max_days = days
                max_ref = p.unit_ref
            monthly = 0
            if hasattr(p, "rentdata"):
                monthly = p.rentdata.current_monthly_fils or p.rentdata.market_monthly_fils or 0
            est_loss = int(monthly * days / 30) if days else 0
            vacant_rows.append(
                {
                    "unit_ref": p.unit_ref,
                    "type": p.type_label,
                    "rent_mo": format_aed(monthly, True),
                    "days_vacant": days,
                    "est_loss": format_aed(est_loss, True),
                    "status": svc.vacancy_status(days),
                }
            )
        vacant_rows.sort(key=lambda x: x["days_vacant"], reverse=True)
        total_loss = sum(
            int(
                (getattr(p, "rentdata", None) and (p.rentdata.current_monthly_fils or 0) or 0)
                * svc.days_vacant(p)
                / 30
            )
            for p in Property.objects.filter(occupancy_status=Property.OCCUPANT_VACANT).select_related(
                "rentdata"
            )
        )
        trend = self._occupancy_trend(request)
        return Response(
            {
                "kpis": {
                    "occupancy_rate": svc.occupancy_rate(),
                    "vacant_units": counts["vacant"],
                    "critical_vacancy": critical,
                    "vacancy_loss_mo": format_aed(svc.vacancy_loss_monthly_fils(), True),
                    "max_days_vacant": max_days,
                    "max_days_unit_ref": max_ref,
                    "avg_vacancy_duration": svc.avg_vacancy_duration(),
                },
                "donut": {
                    "percent": svc.occupancy_rate(),
                    "occupied": counts["occupied"],
                    "total": counts["total"],
                },
                "category_shares": [
                    {"label": "Luxury Villas", "share_pct": 13, "color": "#60A5FA"},
                    {"label": "Standard Villas", "share_pct": 20, "color": "#FBBF24"},
                    {"label": "Larger Apartments", "share_pct": 33, "color": "#34D399"},
                    {"label": "Standard Flats", "share_pct": 33, "color": "#3B82F6"},
                ],
                "vacant_units": vacant_rows,
                "vacant_total_loss": format_aed(total_loss, True),
                "occupancy_trend": trend,
            }
        )

    def _occupancy_trend(self, request):
        offset = int(request.query_params.get("offset", 0))
        snaps = list(MonthlyOccupancySnapshot.objects.order_by("year", "month"))
        if offset:
            snaps = snaps[offset : offset + 12]
        else:
            snaps = snaps[-12:]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return [
            {
                "month": months[s.month - 1],
                "occupied": s.occupied_count,
                "vacant": s.vacant_count,
            }
            for s in snaps
        ]


class FinancialDashboardView(APIView):
    permission_classes = [IsClientReadOnly]

    def get(self, request):
        wf = fin.waterfall()
        annual = svc.monthly_income_fils() * 12
        assumed = True
        trend = fin.revenue_trend()
        current_mo = trend[-1]["current_fils"] if trend else svc.monthly_income_fils()
        potential_mo = trend[-1]["potential_fils"] if trend else int(svc.market_potential_yearly_fils() / 12)
        bear_mo = trend[-1]["bear_fils"] if trend else int(current_mo * 0.79)
        return Response(
            {
                "kpis": {
                    "annual_income": format_aed(annual, assumed),
                    "market_potential": format_aed(wf["market_potential_fils"], assumed),
                    "go_to_potential": format_aed(svc.go_to_potential_fils(), assumed),
                    "vacancy_cost_mo": format_aed(svc.vacancy_loss_monthly_fils(), assumed),
                    "avg_gross_yield": fin.gross_yield_pct(),
                    "dubai_avg_yield": 6.2,
                    "concentration_pct": svc.concentration_pct(),
                    "net_cashflow": format_aed(wf["net_income_fils"], assumed),
                },
                "revenue_trend": trend,
                "revenue_summary": {
                    "current_mo": format_aed(current_mo, assumed),
                    "potential_mo": format_aed(potential_mo, assumed),
                    "bear_mo": format_aed(bear_mo, assumed),
                },
                "waterfall": wf,
                "yield_by_type": fin.yield_by_type(),
                "scenarios": fin.scenario_chart(),
                "breakdown": fin.breakdown_by_category(),
            }
        )
