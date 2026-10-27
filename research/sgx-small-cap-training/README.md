# SGX small-account trading research — 2026-10-27

Goal: screen **individual SGX shares only** for repeat trading practice within a **S$100** sleeve of a fixed S$200 account. ETFs and REITs excluded. This is a screening experiment, not a buy recommendation or automated order execution.

## Initial result
10 candidate stocks screened using observed reference prices (some 2026-10-26, some website snapshots 2026-10-27). Source and date are retained per row. These are **not verified executable bid/ask prices**. For 100-share lots and conditional commission-free pricing, examples:
- Y92 Thai Beverage: 100 shares S$44; estimated roundtrip cost S$2.20; approx break-even +5.0%.
- BDA PNE Industries: S$37; S$2.19; +5.9%.
- BJZ Koda: S$28; S$2.18; +7.8%.
- A31 Addvalue Technologies: S$10.50; S$2.17; +20.6%.

## Method and limits
- Commission: assumed zero **only if account promotion applies**. Otherwise SGX standard commission may add at least S$0.99 per order.
- Platform fee: max(0.03% of trade amount, S$0.99) per order.
- SGX trading + clearing fees: 0.0075% + 0.0325% of amount.
- GST: 9% on listed fees.
- Roundtrip fee is estimated as twice entry fees at unchanged price; actual exit fees vary with sale proceeds. Spread, slippage, stamp duty (if any), corporate actions and other account-specific costs not modeled.
- Screening assumes a **100-share board lot** for these candidates; verify lot size in the trading app. A stock's low price does not make it safe or liquid. Thin order books and tick-size effects can dominate fees.
- Price source: https://sginvestors.io/market/sgx-top-volume and https://stockanalysis.com/list/singapore-exchange/
- Fee sources: https://www.moomoo.com/sg/support/topic5_118 and https://www.moomoo.com/sg/learn/moomoo-singapore-fees-and-pricing

## Next research gates (NOT completed)
1. Verify latest price, bid/ask spread, volume and 100-share lot with Moomoo quote screen.
2. Retrieve latest annual/interim financial statements, cash flow, debt, going-concern qualifications, dilution and corporate actions.
3. Recalculate optimal integer lot quantity within S$100 **including fees**, and break-even using actual bid/ask and realistic exit fees.
4. Define trade hypothesis, maximum loss and exit rules; log every executed trade with fees.

Run `python screen.py` to regenerate `screen_results.csv`.
