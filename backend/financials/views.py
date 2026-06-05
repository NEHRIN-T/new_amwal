from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import FinancialAnalystRole, IsBackendUser
from financials.models import ManagementFeeConfig, ScenarioConfig, ScenarioYearProjection
from properties.models import Property


class FeeConfigView(APIView):
    permission_classes = [IsBackendUser, FinancialAnalystRole]

    def get(self, request):
        cfg = ManagementFeeConfig.objects.order_by("-effective_from").first()
        if not cfg:
            return Response({})
        return Response(
            {
                "fee_type": cfg.fee_type,
                "fee_percentage": float(cfg.fee_percentage),
                "fixed_fee_fils": cfg.fixed_fee_fils,
                "effective_from": cfg.effective_from,
            }
        )

    def post(self, request):
        fee_type = request.data.get("fee_type", ManagementFeeConfig.FEE_PERCENT)
        if fee_type not in {ManagementFeeConfig.FEE_PERCENT, ManagementFeeConfig.FEE_FIXED}:
            return Response({"fee_type": "Invalid fee type."}, status=status.HTTP_400_BAD_REQUEST)
        fee_percentage = request.data.get("fee_percentage", 5.8)
        fixed_fee_fils = request.data.get("fixed_fee_fils", 0)
        if fee_percentage is not None and float(fee_percentage) < 0:
            return Response(
                {"fee_percentage": "Fee percentage cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if fixed_fee_fils is not None and int(fixed_fee_fils) < 0:
            return Response(
                {"fixed_fee_fils": "Fixed fee cannot be negative."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.data.get("effective_from"):
            return Response(
                {"effective_from": "Effective from date is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cfg = ManagementFeeConfig.objects.create(
            fee_type=fee_type,
            fee_percentage=fee_percentage,
            fixed_fee_fils=fixed_fee_fils,
            effective_from=request.data.get("effective_from"),
            is_assumed=False,
        )
        return Response({"id": cfg.id})


class ScenarioConfigView(APIView):
    permission_classes = [IsBackendUser, FinancialAnalystRole]

    def get(self, request):
        data = []
        for cfg in ScenarioConfig.objects.all():
            data.append(
                {
                    "scenario": cfg.scenario,
                    "occupancy_pct": float(cfg.occupancy_pct),
                    "rent_correction_pct": float(cfg.rent_correction_pct),
                    "growth_rate_pct": float(cfg.growth_rate_pct),
                    "description": cfg.description,
                    "projections": list(
                        cfg.projections.values("year_index", "revenue_fils")
                    ),
                }
            )
        return Response(data)

    def put(self, request):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of scenarios."}, status=status.HTTP_400_BAD_REQUEST)
        for item in request.data:
            if item.get("scenario") not in dict(ScenarioConfig.SCENARIO_CHOICES):
                return Response({"scenario": "Invalid scenario."}, status=status.HTTP_400_BAD_REQUEST)
            occupancy_pct = float(item["occupancy_pct"])
            rent_correction_pct = float(item.get("rent_correction_pct", 0))
            growth_rate_pct = float(item.get("growth_rate_pct", 0))
            if not 0 <= occupancy_pct <= 100:
                return Response(
                    {"occupancy_pct": "Occupancy must be between 0 and 100."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not -50 <= rent_correction_pct <= 100:
                return Response(
                    {"rent_correction_pct": "Rent correction must be between -50 and 100."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cfg, _ = ScenarioConfig.objects.update_or_create(
                scenario=item["scenario"],
                defaults={
                    "occupancy_pct": occupancy_pct,
                    "rent_correction_pct": rent_correction_pct,
                    "growth_rate_pct": growth_rate_pct,
                    "description": item.get("description", ""),
                    "is_assumed": False,
                },
            )
            for proj in item.get("projections", []):
                ScenarioYearProjection.objects.update_or_create(
                    scenario=cfg,
                    year_index=proj["year_index"],
                    defaults={"revenue_fils": proj["revenue_fils"], "is_assumed": False},
                )
        return Response({"ok": True})


class ValuationBulkView(APIView):
    permission_classes = [IsBackendUser, FinancialAnalystRole]

    def post(self, request):
        for item in request.data.get("valuations", []):
            value = int(item["estimated_value_fils"])
            if value < 0:
                return Response(
                    {"estimated_value_fils": "Estimated value cannot be negative."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Property.objects.filter(unit_ref=item["unit_ref"]).update(
                estimated_value_fils=value,
                valuation_date=item.get("valuation_date"),
                valuation_source=item.get("valuation_source", "internal"),
                is_assumed=False,
            )
        return Response({"ok": True})
