from datetime import date
from django.db.models import Count, Sum

from properties.models import Property
from rents.models import RentData

from core.gap import GAP_CRITICAL, GAP_REVIEW, gap_status_from_fils


def vacancy_status(days):
    if days > 60:
        return "critical"
    if days > 30:
        return "monitor"
    return "ok"


def days_vacant(prop):
    if prop.occupancy_status != Property.OCCUPANT_VACANT or not prop.vacancy_start_date:
        return 0
    return max(0, (date.today() - prop.vacancy_start_date).days)


def active_properties():
    return Property.objects.filter(status=Property.STATUS_ACTIVE)


def portfolio_counts():
    qs = active_properties()
    total = qs.count()
    occupied = qs.filter(occupancy_status=Property.OCCUPIED).count()
    vacant = qs.filter(occupancy_status=Property.OCCUPANT_VACANT).count()
    return {"total": total, "occupied": occupied, "vacant": vacant}


def occupancy_rate():
    c = portfolio_counts()
    if c["total"] == 0:
        return 0.0
    return round(c["occupied"] / c["total"] * 100, 1)


def monthly_income_fils():
    total = 0
    for rent in RentData.objects.filter(
        property__status=Property.STATUS_ACTIVE,
        property__occupancy_status=Property.OCCUPIED,
    ).select_related("property"):
        total += rent.current_monthly_fils or 0
    return total


def rent_leakage_yearly_fils():
    total = 0
    for rent in RentData.objects.select_related("property").filter(
        property__status=Property.STATUS_ACTIVE
    ):
        gap = (rent.market_annual_fils or 0) - (rent.current_annual_fils or 0)
        if gap > 0:
            total += gap
    return total


def market_potential_yearly_fils():
    return (
        RentData.objects.filter(property__status=Property.STATUS_ACTIVE).aggregate(
            s=Sum("market_annual_fils")
        )["s"]
        or 0
    )


def go_to_potential_fils():
    vacancy_recovery = 0
    for prop in active_properties().filter(occupancy_status=Property.OCCUPANT_VACANT):
        try:
            rent = prop.rentdata
            vacancy_recovery += rent.market_annual_fils or rent.current_annual_fils or 0
        except RentData.DoesNotExist:
            pass
    return vacancy_recovery + rent_leakage_yearly_fils()


def vacancy_loss_monthly_fils():
    total = 0
    for prop in active_properties().filter(occupancy_status=Property.OCCUPANT_VACANT):
        try:
            rent = prop.rentdata
            monthly = rent.current_monthly_fils or rent.market_monthly_fils or 0
            days = days_vacant(prop)
            total += int(monthly * days / 30) if days else monthly
        except RentData.DoesNotExist:
            pass
    return total


def avg_vacancy_duration():
    durations = [
        days_vacant(p)
        for p in active_properties().filter(occupancy_status=Property.OCCUPANT_VACANT)
    ]
    if not durations:
        return 0
    return int(sum(durations) / len(durations))


def composition_by_type():
    qs = active_properties().values("property_type").annotate(count=Count("id"))
    total = portfolio_counts()["total"] or 1
    colors = {
        Property.TYPE_LX_VILLA: "#60A5FA",
        Property.TYPE_STD_VILLA: "#FBBF24",
        Property.TYPE_LARGER_APT: "#34D399",
        Property.TYPE_STD_FLAT: "#3B82F6",
    }
    result = []
    for row in qs:
        result.append(
            {
                "type": row["property_type"],
                "label": dict(Property.TYPE_CHOICES)[row["property_type"]],
                "count": row["count"],
                "percent": round(row["count"] / total * 100),
                "color": colors.get(row["property_type"], "#94A3B8"),
            }
        )
    return result


def occupancy_by_category():
    types = [
        (Property.TYPE_LX_VILLA, "Luxury Villas", "#60A5FA"),
        (Property.TYPE_STD_VILLA, "Standard Villas", "#34D399"),
        (Property.TYPE_LARGER_APT, "Larger Apartments", "#2DD4BF"),
        (Property.TYPE_STD_FLAT, "Standard Flats", "#93C5FD"),
    ]
    rows = []
    for ptype, label, color in types:
        qs = active_properties().filter(property_type=ptype)
        total = qs.count()
        occ = qs.filter(occupancy_status=Property.OCCUPIED).count()
        pct = round(occ / total * 100) if total else 0
        rows.append(
            {
                "label": label,
                "occupied": occ,
                "total": total,
                "percent": pct,
                "display": f"{occ}/{total} - {pct}%",
                "color": color,
            }
        )
    c = portfolio_counts()
    pct = round(c["occupied"] / c["total"] * 100) if c["total"] else 0
    rows.append(
        {
            "label": "Overall Portfolio",
            "occupied": c["occupied"],
            "total": c["total"],
            "percent": pct,
            "display": f"{c['occupied']}/{c['total']} - {pct}%",
            "color": "#F97316",
            "is_overall": True,
        }
    )
    return rows


def rental_intelligence_kpis():
    rents = list(RentData.objects.filter(property__status=Property.STATUS_ACTIVE))
    below = 0
    at_above = 0
    total_gap = 0
    gaps = []
    max_gap = 0
    max_ref = ""
    for r in rents:
        gap = (r.market_annual_fils or 0) - (r.current_annual_fils or 0)
        if gap > 0:
            below += 1
            total_gap += gap
            gaps.append(gap)
            if gap > max_gap:
                max_gap = gap
                max_ref = r.property.unit_ref
        else:
            at_above += 1
    total_units = len(rents) or 1
    avg_gap = int(sum(gaps) / len(gaps)) if gaps else 0
    return {
        "leakage_yearly_fils": total_gap,
        "units_below_market": below,
        "units_below_pct": round(below / total_units * 100),
        "avg_gap_yearly_fils": avg_gap,
        "at_or_above_market": at_above,
        "at_or_above_pct": round(at_above / total_units * 100),
        "max_gap_unit_ref": max_ref,
        "max_gap_yearly_fils": max_gap,
    }


def gap_distribution():
    band_defs = [
        (">60K", 6000001, 999999999999, "#F97316"),
        ("25-60K", 2500000, 6000000, "#22C55E"),
        ("8-25K", 800001, 2499999, "#3B82F6"),
        ("0-8K", 0, 800000, "#A855F7"),
    ]
    counts = {b[0]: 0 for b in band_defs}
    for r in RentData.objects.filter(property__status=Property.STATUS_ACTIVE):
        gap = (r.market_annual_fils or 0) - (r.current_annual_fils or 0)
        if gap <= 0:
            counts["0-8K"] += 1
            continue
        placed = False
        for label, lo, hi, color in band_defs:
            if lo <= gap <= hi:
                counts[label] += 1
                placed = True
                break
        if not placed:
            counts[">60K"] += 1
    return [{"band": label, "count": counts[label], "color": color} for label, lo, hi, color in band_defs]


def gap_by_property_type():
    type_keys = [
        (Property.TYPE_LX_VILLA, "LX Villa"),
        (Property.TYPE_STD_VILLA, "STD Villa"),
        (Property.TYPE_LARGER_APT, "Apt"),
        (Property.TYPE_STD_FLAT, "Flat"),
    ]
    rows = []
    curr_total = 0
    mkt_total = 0
    for ptype, label in type_keys:
        props = list(active_properties().filter(property_type=ptype).select_related("rentdata"))
        curr = sum(getattr(p, "rentdata", None) and p.rentdata.current_annual_fils or 0 for p in props)
        mkt = sum(getattr(p, "rentdata", None) and p.rentdata.market_annual_fils or 0 for p in props)
        curr_total += curr
        mkt_total += mkt
        rows.append({"category": label, "current_fils": curr, "market_fils": mkt})
    rows.append({"category": "Overall", "current_fils": curr_total, "market_fils": mkt_total})
    return rows


def concentration_pct():
    total_val = active_properties().aggregate(s=Sum("estimated_value_fils"))["s"] or 1
    lx_val = (
        active_properties()
        .filter(property_type=Property.TYPE_LX_VILLA)
        .aggregate(s=Sum("estimated_value_fils"))["s"]
        or 0
    )
    return round(lx_val / total_val * 100) if total_val else 0
