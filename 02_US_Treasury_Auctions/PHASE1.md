# Phase 1 — 30-Year Treasury Auction Analysis

## Research question

**Who has been willing to lend to the U.S. government for 30 years, and at what yield?**

Rather than starting from a forecast of a U.S. debt crisis, this project treats the auction yield as the government's marginal long-term funding cost and examines whether the composition of auction buyers changes as that funding cost changes.

## Period

2016-01-01 to present.

## Official source

U.S. Treasury Fiscal Data API — Auctions Query.

Endpoint:

`/v1/accounting/od/auctions_query`

## Core variables

- Auction date
- High yield
- Bid-to-cover ratio
- Offering amount
- Total tendered / accepted
- Primary Dealer accepted amount and share
- Direct Bidder accepted amount and share
- Indirect Bidder accepted amount and share

## Phase 1 workflow

1. Run `fetch_30y_auctions.py`.
2. The script downloads all 30-Year Bond auctions from 2016 onward.
3. It calculates bidder shares using total accepted amount.
4. It writes the clean auction-level CSV to `data/`.
5. Run `analyze_30y_auctions.py`.
6. The analysis produces annual averages, correlations, time-series charts, and yield-versus-buyer-composition scatter plots in `output/`.

## Important interpretation

Primary Dealer / Direct Bidder / Indirect Bidder are auction participation categories, not ultimate beneficial-owner categories. Phase 2 will therefore add Treasury Investor Class Auction Allotments to distinguish investment funds, foreign & international investors, banks, pensions, insurers, dealers, and other investor classes.

## No ex-ante conclusion

The purpose of Phase 1 is exploratory. A rising yield does not by itself demonstrate weak demand or fiscal stress. Bid-to-cover and bidder composition must be examined together with yield and, later, investor-class data.
