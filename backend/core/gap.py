GAP_CRITICAL = 6000000
GAP_REVIEW = 800000


def gap_status_from_fils(gap_fils):
    if gap_fils > GAP_CRITICAL:
        return "critical"
    if gap_fils > GAP_REVIEW:
        return "review"
    return "at_market"
