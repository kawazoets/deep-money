"""Reverse implied POCKETALK stake recoverability at a reference SOURCENEXT price."""
SHARES=138_314_976
PRICE=105  # 2026-10-16 historical reference; not live
POCKETALK_POST_MONEY_JPY_M=31_240
OWNERSHIP=.6882
PARENT_NET_DEBT_2025_12_JPY_M=1052.977  # stale
MARKET_EQUITY_JPY_M=SHARES*PRICE/1e6
HEADLINE_STAKE=POCKETALK_POST_MONEY_JPY_M*OWNERSHIP
GROSS_PROFIT_H1=783
SALES_H1=1485
SGA_H1=1370
print("Historical H1 break-even sales (JPY m):",SGA_H1/(GROSS_PROFIT_H1/SALES_H1))
print("POCKETALK pro-rata financing stake (JPY m):",HEADLINE_STAKE)
for name,ev,cost in [("Recovery",3000,500),("Stagnation",1000,1000),("Restructuring",500,2000)]:
    required=MARKET_EQUITY_JPY_M-ev+PARENT_NET_DEBT_2025_12_JPY_M+cost
    print(name,"required stake (JPY m)",round(required,3),"maximum haircut",round(100*(1-required/HEADLINE_STAKE),2),"%")
