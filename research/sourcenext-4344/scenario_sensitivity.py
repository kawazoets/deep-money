"""Sensitivity only: not a share price forecast. Python 3 stdlib."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHARES = 139_115_100 - 800_124
STAKE = 0.6882
POCKETALK_POSTMONEY_M = 31_240
# Incremental parent net value after correctly removing the carrying value of the
# POCKETALK investment; unknown and deliberately left blank.
PARENT_EX_POCKETALK_M = None
# Incident costs net of insurance, taxes and any amounts already in the parent valuation.
INCIDENT_NET_COST_M = None

rows = []
for haircut in (0, .25, .5, .75, .90):
    stake_value = POCKETALK_POSTMONEY_M * STAKE * (1-haircut)
    for incident in (0, 500, 1000, 2000):
        rows.append({
            "pocketalk_discount_pct": round(haircut*100),
            "incident_cost_assumption_jpy_m": incident,
            "pocketalk_stake_only_jpy_per_share": round(stake_value*1e6/SHARES,2),
            "hypothetical_stake_less_incident_jpy_per_share": round((stake_value-incident)*1e6/SHARES,2),
            "full_group_equity_value_jpy_per_share": "NOT_ESTIMATED",
        })
out = ROOT / "data" / "scenario_sensitivity.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    writer=csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {len(rows)} scenarios to {out}")
print("WARNING: subtracting parent incident cost from stake-only value is a stress illustration, not a takeover valuation.")
print("Full group equity valuation requires parent ex-POCKETALK net assets and liabilities, debt and ownership rights.")
