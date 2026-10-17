"""Sourcenext (4344) verified accounting baseline; all JPY values in millions.
Run: python research/sourcenext-4344/analyze_baseline.py
No external packages required.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
with (HERE / "data" / "financial_baseline.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
data = {(r["period"], r["metric"]): float(r["value"]) for r in rows}
get = lambda period, metric: data[(period, metric)]
cash = get("2026-06-30", "cash_equivalents")
debt = sum(get("2026-06-30", m) for m in ("short_term_borrowings", "current_long_term_debt", "long_term_borrowings", "bonds_payable"))
shares = get("2026-06-30", "issued_shares") - get("2026-06-30", "treasury_shares")
equity = get("2026-06-30", "parent_equity")
ocf = get("2026H1", "operating_cash_flow")
capex = -(get("2026H1", "software_capex") + get("2026H1", "property_capex"))
print(f"Cash equivalents: JPY {cash:,.3f} million")
print(f"Interest-bearing debt: JPY {debt:,.3f} million")
print(f"Net debt (debt - cash equivalents): JPY {debt-cash:,.3f} million")
print(f"Parent equity: JPY {equity:,.3f} million")
print(f"Book equity per share: JPY {equity*1e6/shares:,.2f}")
print(f"Operating cash flow H1: JPY {ocf:,.3f} million")
print(f"Cash flow after PP&E and software capex (not a normalized FCF): JPY {ocf-capex:,.3f} million")
print("WARNING: book equity is not takeover consideration or a share-price floor.")
print("WARNING: working-capital release and nonrecurring transactions affect cash flows.")
