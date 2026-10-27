#!/usr/bin/env python3
"""Illustrative SGX 100-share lot optimization under SGD100 including entry fees.
Prices are historical indicative inputs, not executable bids/offers.
Verify promotion eligibility and broker order preview before trading.
"""
import csv
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

BUDGET = Decimal("100")
STOCKS = [
    ("Y92", "Thai Beverage", "0.440"),
    ("BDA", "PNE Industries", "0.370"),
    ("BJZ", "Koda", "0.280"),
    ("1R6", "Avi-Tech", "0.170"),
    ("A31", "Addvalue", "0.105"),
    ("5PO", "Hiap Tong", "0.095"),
    ("BQN", "BH Global", "0.085"),
    ("5NV", "Chasen", "0.082"),
    ("569", "Vicplas", "0.065"),
    ("594", "CapAllianz", "0.001"),
]
def fee(gross):
    # Promotional commission=0 assumed. Platform min 0.99; SGX 0.04%; GST 9%.
    return (max(gross * Decimal("0.0003"), Decimal("0.99")) +
            gross * Decimal("0.0004")) * Decimal("1.09")

def tick_size(price):
    if price < Decimal("0.20"): return Decimal("0.001")
    if price < Decimal("1"): return Decimal("0.005")
    return Decimal("0.01")

def calculate(ticker, name, price_str):
    p = Decimal(price_str)
    n = 0
    for q in range(100, 100001, 100):
        g = p * q
        if g + fee(g) > BUDGET: break
        n = q
    if not n: return None
    gross = p * n
    entry = fee(gross)
    lo, hi = p, p * 2 + Decimal("3")
    for _ in range(80):
        mid = (lo + hi) / 2
        if mid * n - fee(mid * n) >= gross + entry: hi = mid
        else: lo = mid
    tick = tick_size(p)
    exit_price = (hi / tick).to_integral_value(rounding=ROUND_CEILING) * tick
    return dict(ticker=ticker, name=name, reference_price_sgd=str(p),
                board_lot=100, max_shares=n,
                gross_sgd=f"{gross:.2f}",
                entry_fee_sgd_est=f"{entry:.2f}",
                total_entry_sgd_est=f"{gross+entry:.2f}",
                round_trip_fees_at_flat_price_sgd_est=f"{2*entry:.2f}",
                approx_break_even_pct=f"{2*entry/gross*100:.2f}",
                tick_adjusted_break_even_sell_price_sgd=str(exit_price),
                tick_adjusted_break_even_pct=f"{(exit_price/p-1)*100:.2f}",
                status="ILLUSTRATIVE_ONLY")

rows = [r for args in STOCKS if (r := calculate(*args))]
with (Path(__file__).with_name("optimized_lots.csv")).open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r["ticker"], r["max_shares"], r["total_entry_sgd_est"], r["tick_adjusted_break_even_pct"])
