# SGX liquidity check — 2026-10-27

## Evidence (public delayed / historical, NOT executable quotes)
- Y92 Thai Beverage: Oct 26 close SGD0.440, volume 31.15m; Oct 23 35.27m, Oct 22 6.47m, Oct 21 7.92m, Oct 20 3.2m. Source https://eoddata.com/stockquote/SGX/Y92.htm
- **Data-quality warning:** the same EODData page displayed BID 0.505 / ASK 0.510 despite a 0.440 last close; treat those fields as inconsistent/stale, NOT executable market quotes. Do not calculate spread from them.
- BDA PNE Industries: available StockAnalysis historical records are sparse; Oct 7 2026 10,000 shares, Sep 30 3,000, Sep 28 5,000, Sep 25 700. This suggests limited liquidity and potential exit difficulty. Source https://stockanalysis.com/quote/sgx/BDA/history/
- BJZ Koda: no verified current bid/ask or recent daily volume retrieved in this pass. Mark UNKNOWN, not liquid by assumption.

## Trading gate
Y92 is first for order-book verification, BDA deprioritized for illiquidity, BJZ hold pending liquidity evidence. No buy signal yet.

Broker order preview required for: actual ASK, BID, displayed size at each, board lot, all-in buy fee, sell fee, and cash available. Recompute lots with actual ASK and fee schedule; do not exceed SGD100 total cash outlay. Historical indicative price-based optimization is not an order recommendation.
