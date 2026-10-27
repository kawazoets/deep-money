import csv
from pathlib import Path

BUDGET = 100.0
COMMISSION_FREE = True  # Confirm account eligibility before trading
LOT = 100

rows = []
with open(Path(__file__).with_name("candidates.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        price = float(r["reference_price_sgd"])
        gross = price * LOT
        commission = 0 if COMMISSION_FREE else max(0.0003 * gross, 0.99)
        platform = max(0.0003 * gross, 0.99)
        exchange = 0.0004 * gross
        one_way = (commission + platform + exchange) * 1.09
        roundtrip = 2 * one_way  # Flat-price approximation only
        rows.append({
            **r,
            "lot_cost_sgd": round(gross, 2),
            "estimated_buy_fees_sgd": round(one_way, 3),
            "estimated_roundtrip_fees_sgd": round(roundtrip, 3),
            "break_even_gain_pct_approx": round(roundtrip / gross * 100, 2),
            "within_budget_including_buy_fees": gross + one_way <= BUDGET,
        })

rows.sort(key=lambda r: (not r["within_budget_including_buy_fees"], r["break_even_gain_pct_approx"]))
with open(Path(__file__).with_name("screen_results.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

for r in rows:
    print(r["ticker"], r["lot_cost_sgd"], r["estimated_roundtrip_fees_sgd"], r["break_even_gain_pct_approx"], r["within_budget_including_buy_fees"])
