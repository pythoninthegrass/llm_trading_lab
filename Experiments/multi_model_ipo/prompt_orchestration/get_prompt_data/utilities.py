import pandas as pd
import json
# =========================================================
# HELPERS
# =========================================================

def parse_date(x):
    try:
        return pd.to_datetime(x).date()
    except:
        return None

def looks_like_spac(name: str, description: str):
    blob = f"{name} {description}".lower()

    keywords = [
        "blank check",
        "spac",
        "acquisition corp",
        "special purpose acquisition company",
    ]

    return any(k in blob for k in keywords)


def looks_shellish(name: str, description: str):
    blob = f"{name} {description}".lower()

    keywords = [
        "shell",
        "holding company",
        "exploration stage",
    ]

    return any(k in blob for k in keywords)


def looks_biotech(name: str, description: str):
    blob = f"{name} {description}".lower()

    keywords = [
        "biotech",
        "pharma",
        "therapeutics",
        "clinical-stage",
        "drug",
    ]

    return any(k in blob for k in keywords)


def cache_key(provider, url, params):
    return f"{provider}:{url}:{json.dumps(params, sort_keys=True)}"

# =========================================================
# CORE SAFE UTILITIES
# =========================================================

def safe_float(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except:
        return None


def safe_int(x):
    try:
        if x is None or x == "":
            return None
        return int(float(x))
    except:
        return None


def first_nonempty(*vals):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        return v
    return None


def parse_date_safe(x):
    try:
        return pd.to_datetime(x).date()
    except:
        return None


# =========================================================
# IPO + MARKET VALIDATION LOGIC
# =========================================================

def is_valid_ipo_date(ipo_date, today):
    if ipo_date is None:
        return False
    if ipo_date > today:
        return False
    return True


def passes_market_cap(mcap, min_mcap):
    return mcap is not None and mcap >= min_mcap


def passes_liquidity(price, avg_vol, min_dollar_vol):
    if price is None or avg_vol is None:
        return False
    return (price * avg_vol) >= min_dollar_vol


# =========================================================
# TICKER HANDLING
# =========================================================

def normalize_ticker(t):
    if not t:
        return ""
    return str(t).upper().strip()


def dedupe_tickers(items):
    seen = set()
    out = []
    for x in items:
        t = normalize_ticker(x)
        if not t or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


# =========================================================
# IPO DATA HELPERS
# =========================================================

def get_listing_date(details, ipo_row):
    return first_nonempty(
        (details or {}).get("list_date"),
        (details or {}).get("ipo_date"),
        (ipo_row or {}).get("listing_date")
    )


def extract_market_cap(details):
    return safe_float(
        first_nonempty(
            (details or {}).get("market_cap"),
            (details or {}).get("mktCap")
        )
    )

# =========================================================
# FORMATTER
# =========================================================


def fmt_billions(x):
    if x is None:
        return "UNKNOWN"

    return f"{x / 1e9:.2f}B"


def fmt_millions(x):
    if x is None:
        return "UNKNOWN"

    return f"{x / 1e6:.1f}M"


def format_universe_for_prompt(companies):

    lines = ["IPO_UNIVERSE_START"]

    for c in companies:
        lines.append(
            f"TICKER={c['ticker']} | "
            f"NAME={c['name']} | "
            f"IPO={c['listing_date']} | "
            f"MCAP={fmt_billions(c['market_cap'])} | "
            f"PX={c['price']} | "
            f"ATR={c['atr']} | "
            f"VOL={fmt_millions(c['avg_volume'])} | "
            f"DOLLAR_VOL={fmt_millions(c['dollar_volume'])} | "
            f"MOM_1M={c['mom_1m']}% | "
            f"MOM_3M={c['mom_3m']}% | "
            f"SECTOR={c['sector']} | "
            f"FLAGS={','.join(c['flags']) if c['flags'] else 'NONE'} | "
            f"FIN=revenue:{fmt_billions(c['revenue'])}, "
            f"net_income:{fmt_billions(c['net_income'])}, "
            f"cash:{fmt_billions(c['cash'])}, "
            f"debt:{fmt_billions(c['debt'])}, "
            f"operating_cash_flow:{fmt_billions(c['ocf'])} | "
            f"DESC={truncate(c['description'])}"
        )

    lines.append("IPO_UNIVERSE_END")

    return "\n".join(lines)

# =========================================================
# SCORING + RANKING
# =========================================================

def score_company(c):
    mcap = c.get("market_cap") or 0
    liq = c.get("dollar_volume") or 0
    mom = c.get("momentum") or 0

    return (mcap / 1e9) + (liq / 1e7) + mom


# =========================================================
# FORMATTING
# =========================================================

def format_universe_line(c):
    return (
        f"TICKER={c.get('ticker')} | "
        f"MCAP={c.get('market_cap')} | "
        f"VOL={c.get('avg_volume')} | "
        f"MOM={c.get('momentum')} | "
        f"FLAGS={','.join(c.get('flags', [])) or 'NONE'}"
    )

def truncate(text, limit=200):
    if not text:
        return ""
    text = str(text).strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "..."