# Final research synthesis — SOURCENEXT (4344)
Research cutoff: 2026-10-17. **Completed conditional scenario framework, not a market-price forecast or investment recommendation.**

## Question answered

How could parent shareholder residual value change under POCKETALK sale/financing discounts, standalone business outcomes and October 2026 data-incident costs?

## Verified facts and scope

- 2026-06-30 POCKETALK post-money equity valuation announced: JPY 31,240m.
- SOURCENEXT disclosed 68.82% ownership at that financing.
- **Correct multiplication:** 31,240 × 0.6882 = **JPY 21,499.368m**. Previous Phase 4/5 text used JPY 21,497.368m; **this was an arithmetic error of JPY 2m**, corrected in the final model.
- Parent-only 2025-12-31 borrowings less cash: JPY 1,052.977m. **This is NOT current October 2026 debt.**
- 2026-06-30 outstanding common shares excluding treasury: 138,314,976.
- 2025-12 parent standalone operating profit +274.099m in a 9-month fiscal year, versus approximately -220m in 2026 H1. Not directly comparable.
- 2026-10-15 data incident: up to 22,519,960 records potentially affected; confirmed financial impact and unique individuals unknown.
- 2026-10-16 share-price reference JPY 105 from prior research; this is a historical comparator, not a live quote.

## Final 4 scenarios (JPY million unless per-share)

| Case | POCKETALK stake haircut | Parent business EV | Incremental net incident cost | Parent historical net debt | Residual equity | JPY/share | vs JPY105 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A Recovery | 25% | 3,000 | 500 | 1,052.977 | 17,571.549 | 127.04 | +21.0% |
| B Stagnation | 50% | 1,000 | 1,000 | 1,052.977 | 9,696.707 | 70.11 | -33.2% |
| C Distressed restructuring | 75% | 500 | 2,000 | 1,052.977 | 2,821.865 | 20.40 | -80.6% |
| D Severe impairment | 90% | 0 | 3,000 | 1,052.977 | -1,903.040 | 0.00* | -100% |

*Zero means negative modeled residual value floored at zero as a limited-liability illustration; it is **not a prediction of a zero share quote or insolvency**.

**All POCKETALK discounts, parent EVs and incident cost amounts are hypothetical stress inputs.** No objective probability is assigned. B is a convenient central *scenario*, not an evidence-based expected outcome. Financing valuation is not realizable proceeds. The model assumes zero for unknown taxes, investor preferences, guarantees, transaction costs, unmodeled nonoperating assets/liabilities and dilution. These assumptions can materially change results.

## What this research actually establishes

1. POCKETALK financing-implied stake value is material relative to SOURCENEXT's listed equity value. This may be an asset-value dislocation, but is **not proof of an undervalued stock** because transferability and investor rights remain unverified.
2. Parent-only business had positive operating profit in FY2025's nine months, but losses in H1 2026. A stable annual parent EBIT recovery is unproven.
3. The incident is not an independently quantified liability yet. Permanent customer attrition may damage normalized enterprise value beyond one-off response expenses.
4. The most consequential unknown is **realizable POCKETALK stake value net of rights and claims**, followed by updated parent debt and normalized parent earnings.
5. No evidence supports a firm lower bound, takeover offer, specific acquisition timetable, or forecast scenario probabilities.

## Stop rule and triggers to revisit

Research is concluded at this stage. Reopen only upon a material **new primary disclosure**: POCKETALK cap table/security rights, parent-only interim accounts, actual incident costs/customer attrition, refinancing/covenant event, binding takeover bid, asset sale, or new quarterly earnings. Avoid repeating disclosure searches without such a trigger.

## Primary sources

- [SOURCENEXT IR financial results archive](https://www.sourcenext.co.jp/ir-english/library/summary/)
- [SOURCENEXT annual reports](https://www.sourcenext.co.jp/ir-english/library/annual/)
- [2026 half-year EDINET report, S100YULA](https://ssl4.eir-parts.net/doc/4344/yuho_pdf/S100YULA/00.pdf)
- [2026-10-15 incident notice](https://www.sourcenext.com/support/i/2026/1015_info/)
- [POCKETALK financing announcement, 2026-06-30](https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260630/20260630583941.pdf)

## Reproducibility

Run `python final_scenarios.py` from the project folder to regenerate `data/final_scenarios.csv`. Python standard library only. All user personal shareholdings and cost bases are deliberately excluded.
