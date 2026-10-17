# Phase 10 — conditional sum-of-parts stress test

Research date: 2026-10-17. **Hypothetical model, not a stock-price forecast.**
JPY million except per-share figures. All input values below are independently variable.

## Inputs and baseline

- 138,314,976 SOURCENEXT shares outstanding excluding treasury as of 2026-06-30.
- POCKETALK June 2026 post-money transaction-implied equity value: 31,240m.
- Parent's then disclosed stake: 68.82%; pro-rata implied stake 21,497.368m.
- Historical 2025-12-31 parent standalone net debt: 1,052.977m. **Not a verified 2026-10 debt balance.**
- Parent operating business enterprise value: hypothetical, not derived from a market multiple.
- Other parent net assets/liabilities, cross-guarantees, tax leakage, investor preference and debt refinancings: **not verified**; model separately as an unquantified adjustment, set to zero solely to show arithmetic.

## Stress scenarios

| Case | POCKETALK stake discount | Parent business EV | Parent net debt assumed | Incident net cost | Other claims/taxes/dilution | Residual equity | Per share |
|---|---:|---:|---:|---:|---:|---:|---:|
| A: headline financing anchor | 0% | 3,000 | 1,053 | 500 | 0 | 22,944 | 165.88 |
| B: 50% POCKETALK haircut | 50% | 2,000 | 1,053 | 1,000 | 0 | 10,696 | 77.33 |
| C: 75% haircut, parent weak | 75% | 500 | 1,053 | 2,000 | 0 | 2,821 | 20.40 |
| D: 90% haircut, parent negative EV | 90% | -500 | 1,053 | 2,000 | 0 | -1,403 | 0.00* |

*Negative arithmetic residual is floored at zero **only as a simplified limited-liability equity illustration**. Actual market prices, debt enforcement, restructuring, insolvency priority, investor rights and potential dilution may differ. Negative EV is a hypothetical business carrying cost; no third party has offered this valuation.

**Important:** Parent operating-business EV and parent net debt must be aligned to the same valuation date and perimeter. These deliberately illustrative scenarios use a dated debt anchor and are **not** estimates of actual October 2026 takeover consideration. The POCKETALK stake financing valuation is not verified realizable value.

## Model formula

Parent existing shareholder residual equity (JPY m) =
POCKETALK equity stake realizable value +
parent operating-business enterprise value +
other nonoperating net assets -
parent-only net debt -
incremental incident net cost -
tax, fees, guarantees and senior investor claims -
value transferred through dilution.

For each scenario, use 138.315m shares unless new issuance is modeled; if new shares are issued, adjust both cash proceeds and share count rather than dividing by the old share count.

## How to interpret

This table demonstrates **why a high subsidiary financing valuation does not guarantee a listed parent stock-price floor**: if only a fraction of the stake valuation is realizable, parent debt, incident costs and poor parent EV can consume the remaining shareholder value.

The illustrative downside values are *conditional stress outputs*, not evidence that the stock will trade at those levels. A company takeover, subsidiary sale, emergency financing, and insolvency are separate paths.

## Priorities

1. Replace invented parent business EV with normalized post-Rosetta Stone profit and comparables.
2. Replace dated parent net debt with a current verified balance and maturity profile.
3. Identify the POCKETALK financing terms and whether its disclosed valuation is comparable to common-share sale proceeds.
4. Quantify incident net costs when company filings disclose them; distinguish cash expense from lost sales.
