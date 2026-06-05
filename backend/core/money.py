"""Money helpers - store fils (1 AED = 100 fils), display with K/M."""


def aed_to_fils(aed):
    return int(round(float(aed) * 100))


def fils_to_aed(fils):
    return fils / 100.0


def format_aed(fils, assumed=False):
    aed = fils_to_aed(fils)
    prefix = "~" if assumed else ""
    if abs(aed) >= 1_000_000:
        val = aed / 1_000_000
        s = f"{val:.2f}".rstrip("0").rstrip(".")
        return f"{prefix}AED {s}M"
    if abs(aed) >= 1_000:
        return f"{prefix}AED {aed / 1_000:.0f}K"
    return f"{prefix}AED {aed:,.0f}"
