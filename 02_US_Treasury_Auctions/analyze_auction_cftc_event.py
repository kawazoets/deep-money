from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
D=ROOT/"data"; O=ROOT/"output"; O.mkdir(exist_ok=True)

ic=pd.read_csv(D/"investor_class_30y_nominal.csv")
c=pd.read_csv(D/"cftc_long_bond_tff_2016_2026.csv")
ic["issue_date"]=pd.to_datetime(ic["issue_date"])
c["report_date"]=pd.to_datetime(c["report_date"])
for x in ["total_issue","soma_federal_reserve_banks","investment_funds"]:
    ic[x]=pd.to_numeric(ic[x],errors="coerce")
ic["market_issue"]=ic["total_issue"]-ic["soma_federal_reserve_banks"]
ic["investment_funds_pct_ex_soma"]=100*ic["investment_funds"]/ic["market_issue"]

rows=[]
for market,g in c.groupby("market"):
    g=g.sort_values("report_date").copy()
    # For each auction issue date use the last Tuesday CFTC observation on/before
    # the issue date and the next weekly observation after it.
    for _,a in ic.iterrows():
        pre=g[g["report_date"]<=a["issue_date"]].tail(1)
        post=g[g["report_date"]>a["issue_date"]].head(1)
        if pre.empty or post.empty: continue
        p=pre.iloc[0]; q=post.iloc[0]
        rows.append({
            "issue_date":a["issue_date"],"market":market,
            "investment_funds_pct_ex_soma":a["investment_funds_pct_ex_soma"],
            "pre_report_date":p["report_date"],"post_report_date":q["report_date"],
            "d_asset_mgr_net_pct_oi":q["asset_mgr_net_pct_oi"]-p["asset_mgr_net_pct_oi"],
            "d_leveraged_funds_net_pct_oi":q["leveraged_funds_net_pct_oi"]-p["leveraged_funds_net_pct_oi"],
        })
ev=pd.DataFrame(rows)
ev.to_csv(O/"auction_cftc_event_window.csv",index=False)

out=[]
for market,g in ev.groupby("market"):
    for col in ["d_asset_mgr_net_pct_oi","d_leveraged_funds_net_pct_oi"]:
        z=g[["investment_funds_pct_ex_soma",col]].dropna()
        out.append({"market":market,"cftc_weekly_change":col,"n_auctions":len(z),
                    "corr_with_auction_investment_funds_share":z["investment_funds_pct_ex_soma"].corr(z[col])})
res=pd.DataFrame(out)
res.to_csv(O/"auction_cftc_event_correlations.csv",index=False)
print(res.to_string(index=False))
print("\nDescriptive event-window check only; CFTC Tuesday snapshots do not identify auction causality.")
