"""Emit the temporal-severity web artifact from the Mendeley EDSA RTA set.

The make-or-break finding: total crashes peak in rush hour (volume), but the SHARE of
crashes that injure or kill roughly doubles in the deep-night window when EDSA finally
clears and vehicles reach the speed the road is built for. This writes the small JSON the
map's "is speed even the problem?" panel draws, so the chart is computed from real data,
not hand-typed.

Source: data.mendeley.com/datasets/hwbf6n4krw (RTA_EDSA_2007-2016.xls). Download per
research/correlate-crash-refresh.md, then:
  python3 build/overlay/emit_severity_artifact.py <path-to-RTA_EDSA_2007-2016.xls>
Defaults to the last verify-dir copy if no path is given.
"""
import glob
import json
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent
WEBDATA = ROOT / "build" / "web" / "data"

def find_xls():
    if len(sys.argv) > 1:
        return sys.argv[1]
    hits = sorted(glob.glob(str(ROOT / "tmp" / "verify-*" / "RTA_EDSA_2007-2016.xls")))
    if not hits:
        sys.exit("EDSA xls not found; pass the path (see research/correlate-crash-refresh.md)")
    return hits[-1]

df = pd.read_excel(find_xls())
dt = pd.to_datetime(df["DATETIME_PST"], errors="coerce")
hour = dt.dt.hour
kt = pd.to_numeric(df["killed_total"], errors="coerce").fillna(0)
it = pd.to_numeric(df["injured_total"], errors="coerce").fillna(0)
casualty = ((kt > 0) | (it > 0)).astype(int)

by_hour = []
for h in range(24):
    m = hour == h
    n = int(m.sum())
    nc = int(casualty[m].sum())
    by_hour.append({"hour": h, "n": n, "casualty": nc,
                    "casualty_share_pct": round(100 * nc / max(n, 1), 2)})

peak_h = [7, 8, 9, 17, 18, 19]
night_h = [0, 1, 2, 3, 4]
pk, ni = hour.isin(peak_h), hour.isin(night_h)
c_ni, n_ni = int(casualty[ni].sum()), int(ni.sum())
c_pk, n_pk = int(casualty[pk].sum()), int(pk.sum())
chi2, p, _, _ = stats.chi2_contingency([[c_ni, n_ni - c_ni], [c_pk, n_pk - c_pk]])

art = {
    "source": "Mendeley EDSA RTA 2007-2016 (MMDA / UP Diliman), n=%d crashes" % len(df),
    "corridor": "EDSA, Metro Manila",
    "by_hour": by_hour,
    "peak": {"hours": peak_h, "crashes": n_pk, "per_hour": round(n_pk / len(peak_h)),
             "casualty_share_pct": round(100 * c_pk / n_pk, 1)},
    "night": {"hours": night_h, "crashes": n_ni, "per_hour": round(n_ni / len(night_h)),
              "casualty_share_pct": round(100 * c_ni / n_ni, 1)},
    "relative_risk_night_over_peak": round((c_ni / n_ni) / (c_pk / n_pk), 2),
    "chi2": round(chi2, 1), "p_value": float(f"{p:.1e}"),
    "n_casualty": int(casualty.sum()), "n_fatal": int((kt > 0).sum()),
    "disclaimer": "Statistical indicators derived from public data. Patterns may have legitimate explanations."
}
(WEBDATA / "severity_by_hour.json").write_text(json.dumps(art, indent=2))
print("peak casualty share %.1f%% (%d/hr) vs night %.1f%% (%d/hr) | RR %.2f | chi2=%.0f p=%.1e"
      % (art["peak"]["casualty_share_pct"], art["peak"]["per_hour"],
         art["night"]["casualty_share_pct"], art["night"]["per_hour"],
         art["relative_risk_night_over_peak"], art["chi2"], art["p_value"]))
print("wrote", WEBDATA / "severity_by_hour.json")
