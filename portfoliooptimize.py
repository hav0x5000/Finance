import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math as mt
import itertools as iter

def main():
	symbols = ['C', 'GS', 'IBM', 'HNZ']	#Change this to reflect the securities you want analysis done against
	startdate=dt.datetime(2010, 1, 1)       #Start time of the analysis
	enddate=dt.datetime(2010, 12, 31)	#End time of the analysis
	alloc = np.full((1, len(symbols)), 0.0)
	
	for val in iter.product(np.arange(0, 1.01, 0.1), repeat=len(symbols)):    #This will create the allocationcombinations you need. Change the the interval in arange to make it more granular
		a=np.array(val)
		if (np.sum(a)==1):
			alloc=np.append(alloc, [a], axis=0)  #axis=0 always means rows

	alloc = np.delete(alloc, 0, axis=0)
	rows, columns = alloc.shape

	largest_sharpe=0.0
	sharpe= 0.0
	final_vol=0.0
	final_daily_ret=0.0
	final_cum_ret=0.0

	best_allocation=np.array([0.0, 0.0, 0.0, 0.0])
	
	for allocation in xrange(0, rows):
		print "Allocation being tested: " + str(alloc[allocation])
		vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, symbols, alloc[allocation])
		if (sharpe>largest_sharpe):
			largest_sharpe=sharpe
			final_vol=vol
			final_daily_ret=daily_ret
			final_cum_ret=cum_ret
			best_allocation = alloc[allocation]

	print "Best Allocation:"
	print(symbols)
	print(best_allocation)
	print "Sharpe Ratio: " + str(largest_sharpe)
	print "Volatility: " + str(final_vol)
	print "Daily Average Return: " + str(final_daily_ret)
	print "Cumulative Return: " + str(final_cum_ret)



	

def simulate(startdate, enddate, symbols, alloc):
	ls_symbols = symbols
	lf_alloc = alloc
	dt_start = startdate
	dt_end = enddate
	dt_timeofday=dt.timedelta(hours=16)
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

	c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ls_keys = ['open', 'close', 'high', 'low', 'volume']
	ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))
	for s_key in ls_keys:
        	d_data[s_key] = d_data[s_key].fillna(method='ffill')
        	d_data[s_key] = d_data[s_key].fillna(method='bfill')
        	d_data[s_key] = d_data[s_key].fillna(1.0)
	
	na_price = d_data['close'].values
	
	na_normalized_price = na_price/na_price[0, :]
	na_port = na_normalized_price*lf_alloc
	na_port_daily_totals = np.sum(na_port, axis = 1)
	na_rets = na_port_daily_totals.copy()
	tsu.returnize0(na_rets)

	vol = np.std(na_rets)
	daily_ret = np.mean(na_rets)
	sharpe = mt.sqrt(252)*daily_ret/vol
	cum_ret = na_port_daily_totals[-1]/na_port_daily_totals[0]

	return (vol, daily_ret, sharpe, cum_ret)


if __name__ == '__main__':
	main()	
