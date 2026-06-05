from django.db.models import Sum

from financials.models import ManagementFeeConfig, MonthlyRevenueSnapshot, ScenarioConfig
from properties import services as portfolio
from properties.models import Property


def latest_fee_config():
    return ManagementFeeConfig.objects.order_by("-effective_from").first()


def management_fees_yearly_fils():
    cfg = latest_fee_config()
    annual_income = portfolio.monthly_income_fils() * 12
    if not cfg:
        return int(annual_income * 0.058)
    if cfg.fee_type == ManagementFeeConfig.FEE_PERCENT:
        return int(annual_income * float(cfg.fee_percentage) / 100)
    return cfg.fixed_fee_fils * Property.objects.filter(status=Property.STATUS_ACTIVE).count()


def waterfall():
    market = portfolio.market_potential_yearly_fils()
    vacancy = int(portfolio.vacancy_loss_monthly_fils() * 12)
    rent_gap = portfolio.rent_leakage_yearly_fils()
    mgmt = management_fees_yearly_fils()
    net = market - vacancy - rent_gap - mgmt
    return {
        "market_potential_fils": market,
        "vacancy_loss_fils": vacancy,
        "rent_gap_fils": rent_gap,
        "management_fees_fils": mgmt,
        "net_income_fils": net,
    }


def gross_yield_pct():
    total_income = portfolio.monthly_income_fils() * 12
    total_value = Property.objects.filter(status=Property.STATUS_ACTIVE).aggregate(
        s=Sum("estimated_value_fils")
    )["s"] or 1
    return round(total_income / total_value * 100, 1) if total_value else 0


def yield_by_type():
    types = [
        (Property.TYPE_LX_VILLA, "Luxury Villas", "~AED 8.5M avg"),
        (Property.TYPE_STD_VILLA, "Standard Villas", "~AED 3.5M avg"),
        (Property.TYPE_LARGER_APT, "Larger Apartments", "~AED 1.5M avg"),
        (Property.TYPE_STD_FLAT, "Standard Flats", "~AED 780K avg"),
    ]
    rows = []
    for ptype, label, val_hint in types:
        props = Property.objects.filter(property_type=ptype, status=Property.STATUS_ACTIVE)
        income = 0
        value = 0
        for p in props.select_related("rentdata"):
            if hasattr(p, "rentdata"):
                income += p.rentdata.current_annual_fils or 0
            value += p.estimated_value_fils or 0
        yld = round(income / value * 100, 1) if value else 0
        rows.append({"label": label, "yield_pct": yld, "valuation_hint": val_hint})
    return rows


def breakdown_by_category():
    types = [
        (Property.TYPE_LX_VILLA, "Luxury Villas"),
        (Property.TYPE_STD_VILLA, "Standard Villas"),
        (Property.TYPE_LARGER_APT, "Larger Apartments"),
        (Property.TYPE_STD_FLAT, "Standard Flats"),
    ]
    rows = []
    totals = {"units": 0, "occ": 0, "curr": 0, "mkt": 0, "mo": 0, "ann": 0, "leak": 0}
    for ptype, label in types:
        props = list(
            Property.objects.filter(property_type=ptype, status=Property.STATUS_ACTIVE).select_related(
                "rentdata"
            )
        )
        units = len(props)
        occ = sum(1 for p in props if p.occupancy_status == Property.OCCUPIED)
        curr = sum(getattr(p, "rentdata", None) and p.rentdata.current_annual_fils or 0 for p in props)
        mkt = sum(getattr(p, "rentdata", None) and p.rentdata.market_annual_fils or 0 for p in props)
        mo = curr // 12 if curr else 0
        leak = 0
        for p in props:
            if hasattr(p, "rentdata"):
                leak += max(
                    0, (p.rentdata.market_annual_fils or 0) - (p.rentdata.current_annual_fils or 0)
                )
        occ_pct = round(occ / units * 100) if units else 0
        val_sum = sum(p.estimated_value_fils for p in props)
        yld = round(curr / val_sum * 100, 1) if val_sum else 0
        rows.append(
            {
                "category": label,
                "units": units,
                "occupied": occ,
                "occ_pct": occ_pct,
                "curr_rent_fils": curr,
                "mkt_rent_fils": mkt,
                "monthly_income_fils": mo,
                "annual_income_fils": curr,
                "leakage_fils": leak,
                "yield_pct": yld,
            }
        )
        totals["units"] += units
        totals["occ"] += occ
        totals["curr"] += curr
        totals["mkt"] += mkt
        totals["mo"] += mo
        totals["ann"] += curr
        totals["leak"] += leak
    total_units = totals["units"] or 1
    rows.append(
        {
            "category": "TOTAL",
            "units": totals["units"],
            "occupied": totals["occ"],
            "occ_pct": round(totals["occ"] / total_units * 100),
            "curr_rent_fils": totals["curr"],
            "mkt_rent_fils": totals["mkt"],
            "monthly_income_fils": totals["mo"],
            "annual_income_fils": totals["ann"],
            "leakage_fils": totals["leak"],
            "yield_pct": gross_yield_pct(),
            "is_total": True,
        }
    )
    return rows


def revenue_trend():
    data = list(
        MonthlyRevenueSnapshot.objects.filter(
            scenario=MonthlyRevenueSnapshot.SCENARIO_CURRENT
        ).order_by("year", "month")[:12]
    )
    potential = list(
        MonthlyRevenueSnapshot.objects.filter(
            scenario=MonthlyRevenueSnapshot.SCENARIO_POTENTIAL
        ).order_by("year", "month")[:12]
    )
    bear = list(
        MonthlyRevenueSnapshot.objects.filter(
            scenario=MonthlyRevenueSnapshot.SCENARIO_BEAR
        ).order_by("year", "month")[:12]
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    result = []
    for i, snap in enumerate(data):
        result.append(
            {
                "month": month_names[snap.month - 1],
                "year": snap.year,
                "current_fils": snap.amount_fils,
                "potential_fils": potential[i].amount_fils if i < len(potential) else 0,
                "bear_fils": bear[i].amount_fils if i < len(bear) else 0,
                "is_assumed": snap.is_assumed,
            }
        )
    return result


def scenario_chart():
    result = []
    for cfg in ScenarioConfig.objects.all():
        projections = list(cfg.projections.order_by("year_index"))
        result.append(
            {
                "scenario": cfg.scenario,
                "description": cfg.description,
                "occupancy_pct": float(cfg.occupancy_pct),
                "years": [
                    {"year": "YR %s" % p.year_index, "revenue_fils": p.revenue_fils}
                    for p in projections
                ],
            }
        )
    return result
