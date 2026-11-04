import numpy as np
def incremental_profit(a,b,c,d): return 55*(np.asarray(b)-np.asarray(a))-(d/100)*np.asarray(c)*(1-np.exp(-np.asarray(b)))
