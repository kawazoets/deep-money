"""Financial cyber incident research: validate and chart a manually verified event CSV.
Usage: python financial_cyber_research.py events.csv
Columns: event_id,event_date,entity,country,sector,incident_type,loss_usd,source_url,verified
verified: true/false; loss_usd blank if unknown. One row per event, not per article.
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

COLUMNS=['event_id','event_date','entity','country','sector','incident_type','loss_usd','source_url','verified']

def main(path):
    df=pd.read_csv(path,dtype={'event_id':str})
    missing=set(COLUMNS)-set(df.columns)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    df['event_date']=pd.to_datetime(df['event_date'],errors='coerce')
    df['loss_usd']=pd.to_numeric(df['loss_usd'],errors='coerce')
    df['verified']=df['verified'].astype(str).str.lower().eq('true')
    df=df[df.verified & df.event_date.notna() & df.source_url.notna()].copy()
    df=df[df.event_date.between('2024-01-01','2026-11-06')]
    df=df.drop_duplicates('event_id')
    df['month']=df.event_date.dt.to_period('M').astype(str)
    df['year']=df.event_date.dt.year
    out=Path(path).parent
    monthly=df.groupby(['month','sector']).size().unstack(fill_value=0)
    monthly.to_csv(out/'monthly_counts.csv')
    df.groupby('sector').agg(events=('event_id','size'),known_loss_usd=('loss_usd','sum'),loss_disclosed=('loss_usd','count')).to_csv(out/'sector_summary.csv')
    if not monthly.empty:
        monthly.plot(kind='bar',stacked=True,figsize=(13,6))
        plt.title('Verified publicly reported financial cyber incidents (not global totals)')
        plt.ylabel('Recorded incidents');plt.xlabel('Month')
        plt.tight_layout();plt.savefig(out/'monthly_incidents.png',dpi=160)
    print('Verified events:',len(df),'| Warning: source coverage and reporting bias prevent population-level inference.')
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: python financial_cyber_research.py events.csv')
    main(sys.argv[1])
