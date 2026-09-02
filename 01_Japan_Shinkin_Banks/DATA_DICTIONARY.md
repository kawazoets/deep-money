# Data Dictionary

## Japan Shinkin Banks — Interest Rate Risk Project

This file defines the variables collected for the Deep Money Japan Shinkin Banks research project.

The dataset is designed to answer one central question:

**What happens to the balance sheet of each shinkin bank when interest rates rise?**

---

## 1. Institution Information

| Variable | Description |
|---|---|
| shinkin_name | Name of the shinkin bank |
| prefecture | Prefecture |
| fiscal_year | Fiscal year |
| disclosure_source | Source disclosure document |
| disclosure_url | URL of source document |

---

## 2. Balance Sheet

| Variable | Description |
|---|---|
| total_assets | Total assets |
| deposits | Deposits and installment savings |
| loans | Loans and bills discounted |
| securities | Total securities |
| government_bonds | Japanese government bonds |
| local_government_bonds | Local government bonds |
| corporate_bonds | Corporate bonds |
| stocks | Stocks |
| other_securities | Other securities |
| net_assets | Net assets |
| capital | Regulatory capital / self-capital where available |

---

## 3. Securities Valuation

| Variable | Description |
|---|---|
| held_to_maturity_bonds | Held-to-maturity bonds |
| available_for_sale_securities | Other securities / available-for-sale securities |
| unrealized_gain_loss_total | Total unrealized gain/loss on securities |
| unrealized_gain_loss_bonds | Unrealized gain/loss on bonds |
| securities_book_value | Book value of securities |
| securities_market_value | Market value of securities |

---

## 4. Profitability and Funding

| Variable | Description |
|---|---|
| interest_income | Interest income |
| loan_interest_income | Interest income from loans |
| securities_interest_income | Interest/dividend income from securities |
| interest_expense | Interest expense |
| deposit_interest_expense | Interest paid on deposits |
| net_income | Net income |

---

## 5. Structural Ratios

These variables can be calculated from the collected financial data.

| Variable | Calculation |
|---|---|
| loan_to_deposit_ratio | loans / deposits |
| securities_to_deposit_ratio | securities / deposits |
| securities_to_assets_ratio | securities / total_assets |
| government_bonds_to_securities | government_bonds / securities |
| unrealized_loss_to_capital | unrealized_loss / capital |
| loans_to_assets | loans / total_assets |

---

## 6. Interest Rate Risk — IRRBB

Where available, collect the institution's disclosed Interest Rate Risk in the Banking Book (IRRBB) data.

| Variable | Description |
|---|---|
| delta_eve_up | ΔEVE under upward parallel interest-rate shock |
| delta_eve_down | ΔEVE under downward parallel shock |
| delta_eve_steepener | ΔEVE under steepening scenario |
| delta_eve_max | Maximum disclosed ΔEVE |
| delta_nii_up | ΔNII under upward interest-rate shock |
| delta_nii_down | ΔNII under downward interest-rate shock |
| irrbb_capital | Capital amount used for IRRBB calculation |
| delta_eve_to_capital | Maximum ΔEVE / IRRBB capital |

---

## 7. Interest Rate Shock Scenario

Deep Money will separately test simplified interest-rate scenarios where sufficient data are available.

Initial scenarios:

- Current
- +0.5%
- +1.0%
- +2.0%

The objective is not to predict future interest rates.

The objective is to examine how different balance-sheet structures respond to the same interest-rate shock.

---

## 8. Research Principle

A large securities portfolio does not automatically imply financial weakness.

Interest-rate vulnerability must be evaluated in relation to:

**Securities Exposure × Interest Rate Sensitivity × Capital Absorption × Earnings Capacity × Funding Structure**

The project therefore avoids ranking institutions based on a single financial indicator.
