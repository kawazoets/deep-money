# SGX lot optimization — 2026-10-27

S$100 is the **hard entry cash limit inclusive of estimated purchase fees**, not merely share notional. No extra funds, ETFs, or REITs.

Run `python optimize_lots.py` to regenerate `optimized_lots.csv`.

**Assumptions**: 100-share lots for these sub-S$10 stocks; promotional commission waived; Moomoo SG platform fee max(0.03% trade value, S$0.99), SGX trading+clearing 0.04%, 9% GST. Check actual fee plan and order preview. Tick sizes: <S$0.20 S$0.001, S$0.20–0.995 S$0.005, >=S$1 S$0.01. References: https://www.moomoo.com/sg/learn/moomoo-singapore-fees-and-pricing?lang=en-us ; https://www.sgx.com/securities/trading ; https://rulebook.sgx.com/rulebook/chapter-8-trading-0

**Reference prices are historical indicative inputs**, NOT today's ask/bid or a tradable quote. Flat-price roundtrip fees are an approximation; the script solves a fee-inclusive sell break-even and rounds up to the price tick. It does not include bid-ask spread or slippage.

**Financial risk / liquidity gate**: Do not rank or trade purely by lowest break-even percentage. Verify average volume, executable bid-ask, spreads, recent filings, cash flow, corporate actions and actual broker fees first. Ultra-low-price counters such as 594 have a 100% minimum one-tick gain at S$0.001, making them unsuitable for this approach.

Selected examples: Y92 200 shares ~S$89.12 entry; BDA 200 shares ~S$75.11; BJZ 300 shares ~S$85.12. Each is conditional and not a buy instruction.
