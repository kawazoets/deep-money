"""Final SOURCENEXT conditional SOTP scenarios; not investment price targets."""
import csv
from pathlib import Path
SHARES = 138_314_976
POCKETALK_EQUITY_JPY_M = 31_240.0
PARENT_OWNERSHIP = .6882
STAKE_ANCHOR = POCKETALK_EQUITY_JPY_M * PARENT_OWNERSHIP
PARENT_NET_DEBT_2025_12_JPY_M = 1052.977  # stale historical parent-only data
SCENARIOS = [
    ("A_recovery", .25, 3000., 500.),
    ("B_stagnation", .50, 1000., 1000.),
    ("C_distressed_restructuring", .75, 500., 2000.),
    ("D_severe_impairment", .90, 0., 3000.),
]
rows=[]
for name, discount, parent_ev, incident_cost in SCENARIOS:
    pocketalk_stake = STAKE_ANCHOR * (1-discount)
    residual = pocketalk_stake + parent_ev - PARENT_NET_DEBT_2025_12_JPY_M - incident_cost
    per_share = max(0, residual)*1_000_000/SHARES
    rows.append(dict(scenario=name, pocketalk_stake_discount=discount,
        pocketalk_stake_value_jpy_m=round(pocketalk_stake,3),
        parent_operating_ev_jpy_m=parent_ev,
        parent_net_debt_2025_12_jpy_m=PARENT_NET_DEBT_2025_12_JPY_M,
        hypothetical_incremental_incident_cost_jpy_m=incident_cost,
        residual_equity_jpy_m=round(residual,3),
        limited_liability_value_per_share_jpy=round(per_share,2),
        reference_price_2026_10_16_jpy=105,
        percentage_vs_reference=round((per_share/105-1)*100,2),
        verified_takeover_price="NO"))
out=Path(__file__).resolve().parent/"data"/"final_scenarios.csv"
out.parent.mkdir(parents=True,exist_ok=True)
with out.open("w",encoding="utf-8",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
for row in rows: print(row["scenario"],row["limited_liability_value_per_share_jpy"])
