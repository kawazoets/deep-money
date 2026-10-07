from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent; D=ROOT/"data"; O=ROOT/"output"; O.mkdir(exist_ok=True)
fund=pd.read_csv(D/"fed_fund_treasury_holdings_annual.csv")
ic=pd.read_csv(D/"investor_class_30y_nominal.csv")
ic["issue_date"]=pd.to_datetime(ic["issue_date"])
for c in ["total_issue","soma_federal_reserve_banks","investment_funds"]: ic[c]=pd.to_numeric(ic[c],errors="coerce")
ic["year"]=ic.issue_date.dt.year
ic["market_issue"]=ic.total_issue-ic.soma_federal_reserve_banks
a=ic.groupby("year",as_index=False).agg(investment_funds=("investment_funds","sum"),market_issue=("market_issue","sum"))
a["investment_funds_pct_ex_soma"]=100*a.investment_funds/a.market_issue
m=a.merge(fund,on="year",how="left")
m.to_csv(O/"investment_funds_vs_fed_fund_holdings.csv",index=False)

# Compare growth, not claim decomposition: these Fed series cover the whole Treasury market,
# while Investor Class here is 30Y auction allotments.
base=m[m.year==2016].iloc[0]
for c in ["mutual_funds_treasury","hf_domestic_treasury_net","hf_foreign_treasury_net",
          "hf_domestic_government_long","hf_foreign_government_long"]:
    m[c+"_index_2016_100"]=100*m[c]/base[c]
m.to_csv(O/"investment_funds_vs_fed_fund_holdings_indexed.csv",index=False)
print(m[["year","investment_funds_pct_ex_soma","mutual_funds_treasury","hf_domestic_treasury_net",
         "hf_foreign_treasury_net","hf_foreign_government_long","period_type"]].to_string(index=False))
