import pandas as pd
def expected_discount_cost(d,a,p): return d/100*a*p
def select_offers(customers,p0,p10,p20,budget_inr): return pd.Series(["NONE"]*len(customers))
