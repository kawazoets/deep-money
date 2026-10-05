# 02 — U.S. 30-Year Treasury Auctions

## Research question

**Who has been willing to lend to the U.S. government for 30 years, and at what yield?**

Rather than starting from a forecast that a U.S. debt crisis will or will not occur, this project treats the Treasury auction as a funding market. The initial task is to observe how the U.S. government's long-term funding cost and the composition of auction buyers have changed over roughly the last decade.

## Phase 1 — Auction results, 2016–2026

Build one row per 30-Year Treasury Bond auction (including reopenings), with at least:

- Auction date
- Issue date
- CUSIP
- Reopening flag
- Offering amount
- High yield
- Bid-to-cover ratio
- Primary Dealer accepted
- Direct Bidder accepted
- Indirect Bidder accepted
- Total competitive accepted
- Primary Dealer share (%)
- Direct Bidder share (%)
- Indirect Bidder share (%)

Initial comparisons:

1. High Yield × Primary Dealer share
2. High Yield × Direct Bidder share
3. High Yield × Indirect Bidder share
4. High Yield × Bid-to-Cover
5. Changes in buyer composition through time

No crisis hypothesis is imposed in advance. The purpose is to identify unusual changes in the data first.

## Phase 2 — Investor class

If Phase 1 produces useful signals, merge/compare Treasury Investor Class Auction Allotment data to distinguish categories such as:

- Dealers and brokers
- Investment funds
- Foreign and international
- Depository institutions
- Pension / retirement funds and insurance companies
- Individuals / other categories where available

This should help move from auction bidding labels (Primary / Direct / Indirect) toward the economic identity of the buyers.

## Interpretation

A useful working analogy is to view Treasury issuance as the U.S. government's **procurement of funding**. The auction yield is therefore examined as a market-determined funding cost: how much does the government have to pay to procure 30-year money, and which investors supply it at that price?

This is an analytical analogy, not an accounting definition of bond price or government procurement cost.

## Primary sources

- U.S. Treasury / TreasuryDirect — Auction Query
- U.S. Treasury — Investor Class Auction Allotments

TreasuryDirect Auction Query supports CSV, JSON, TSV and XML exports and contains fields including High Yield, Bid-to-Cover Ratio, Primary Dealer Accepted, Direct Bidder Accepted, and Indirect Bidder Accepted.

## Status

- [x] Research question defined
- [x] Repository workspace created
- [ ] Download 2016–2026 30-Year auction data
- [ ] Clean and validate dataset
- [ ] Calculate bidder shares
- [ ] Produce first charts
- [ ] Inspect anomalies before forming the next hypothesis
