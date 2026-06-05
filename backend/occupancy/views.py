from datetime import date

from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.views import APIView

from core.permissions import IsBackendUser, PropertyManagerRole
from occupancy.models import OccupancyHistory
from properties.models import Property
from properties import services as svc
from core.money import format_aed


class OccupancyDashboardView(APIView):
    permission_classes = [IsBackendUser, PropertyManagerRole]

    def get(self, request):
        rows = []
        for p in Property.objects.filter(occupancy_status=Property.OCCUPANT_VACANT).select_related(
            "rentdata"
        ):
            days = svc.days_vacant(p)
            monthly = 0
            if hasattr(p, "rentdata"):
                monthly = p.rentdata.current_monthly_fils or 0
            rows.append(
                {
                    "unit_ref": p.unit_ref,
                    "days_vacant": days,
                    "status": svc.vacancy_status(days),
                    "est_loss_mo": format_aed(int(monthly * days / 30), True),
                    "target_date": p.target_occupancy_date,
                }
            )
        rows.sort(key=lambda x: x["days_vacant"], reverse=True)
        critical = sum(1 for r in rows if r["days_vacant"] > 60)
        monitor = sum(1 for r in rows if 30 < r["days_vacant"] <= 60)
        new = sum(1 for r in rows if r["days_vacant"] <= 30)
        return Response(
            {
                "total_vacant": len(rows),
                "critical": critical,
                "monitor": monitor,
                "new": new,
                "units": rows,
            }
        )


class OccupancyUpdateView(APIView):
    permission_classes = [IsBackendUser, PropertyManagerRole]

    def post(self, request, pk):
        prop = Property.objects.get(pk=pk)
        status = request.data.get("status")
        effective = request.data.get("effective_date", str(date.today()))
        reason = request.data.get("reason", "")
        valid_statuses = {
            Property.OCCUPIED,
            Property.OCCUPANT_VACANT,
            Property.OCCUPANT_RENOVATION,
            Property.OCCUPANT_RESERVED,
        }
        if status not in valid_statuses:
            return Response(
                {"status": "Invalid occupancy status."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(effective, str):
            from datetime import datetime

            try:
                effective = datetime.strptime(effective[:10], "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"effective_date": "Invalid date. Expected YYYY-MM-DD."},
                    status=http_status.HTTP_400_BAD_REQUEST,
                )
        prop.occupancy_status = status
        if status == Property.OCCUPANT_VACANT:
            prop.vacancy_start_date = effective
        elif status == Property.OCCUPIED:
            prop.vacancy_start_date = None
        prop.save()
        OccupancyHistory.objects.create(
            property=prop,
            status=status,
            effective_date=effective,
            reason=reason,
            changed_by=request.user,
        )
        return Response({"ok": True, "unit_ref": prop.unit_ref})
