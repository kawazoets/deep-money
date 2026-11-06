# Financial Cyber Incidents (2024–2026)

Research on publicly documented cyber incidents affecting banks, securities, payment systems, insurers, fintech and crypto platforms.

## Status
Research scaffold only. No incident records have yet been collected or verified. The CSV is an empty template, not a global dataset.

## Method
One row per incident (not per news article); include a primary or credible corroborating source URL. Separate attempted attacks from confirmed breaches and disclosed losses from unknown amounts. Counts of reported incidents cannot be interpreted as worldwide incidence without adjusting for reporting and coverage bias.

## Run
Install Python dependencies: `pip install pandas matplotlib`.

Copy `events_template.csv` to `events.csv`, add verified records, then run `python financial_cyber_research.py events.csv`.

Outputs: `monthly_counts.csv`, `sector_summary.csv`, and, when data exist, `monthly_incidents.png`.
