"""MC2-P1: Market simulator. 			  		 			 	 	 		 		 	  		   	  			  	
 			  		 			 	 	 		 		 	  		   	  			  	
Copyright 2018, Georgia Institute of Technology (Georgia Tech) 			  		 			 	 	 		 		 	  		   	  			  	
Atlanta, Georgia 30332 			  		 			 	 	 		 		 	  		   	  			  	
All Rights Reserved 			  		 			 	 	 		 		 	  		   	  			  	
 			  		 			 	 	 		 		 	  		   	  			  	
Template code for CS 4646/7646 			  		 			 	 	 		 		 	  		   	  			  	
 			  		 			 	 	 		 		 	  		   	  			  	
Georgia Tech asserts copyright ownership of this template and all derivative 			  		 			 	 	 		 		 	  		   	  			  	
works, including solutions to the projects assigned in this course. Students 			  		 			 	 	 		 		 	  		   	  			  	
and other users of this template code are advised not to share it with others 			  		 			 	 	 		 		 	  		   	  			  	
or to make it available on publicly viewable websites including repositories 			  		 			 	 	 		 		 	  		   	  			  	
such as github and gitlab.  This copyright statement should not be removed 			  		 			 	 	 		 		 	  		   	  			  	
or edited. 			  		 			 	 	 		 		 	  		   	  			  	
 			  		 			 	 	 		 		 	  		   	  			  	
We do grant permission to share solutions privately with non-students such 			  		 			 	 	 		 		 	  		   	  			  	
as potential employers. However, sharing with other current or future 			  		 			 	 	 		 		 	  		   	  			  	
students of CS 7646 is prohibited and subject to being investigated as a 			  		 			 	 	 		 		 	  		   	  			  	
GT honor code violation. 			  		 			 	 	 		 		 	  		   	  			  	
 			  		 			 	 	 		 		 	  		   	  			  	
-----do not edit anything above this line--- 			  		 			 	 	 		 		 	  		   	  			  	
 			  		 			 	 	 		 		 	  		   	  			  	
Student Name: Tucker Balch (replace with your name) 			  		 			 	 	 		 		 	  		   	  			  	
GT User ID: gyan31 (replace with your User ID) 			  		 			 	 	 		 		 	  		   	  			  	
GT ID: 903272167 (replace with your GT ID) 			  		 			 	 	 		 		 	  		   	  			  	
""" 			  		 			 	 	 		 		 	  		   	  			  	
import pandas as pd 			  		 			 	 	 		
import numpy as np 			  		 			 	 	 		
import datetime as dt 			  		 			 	 	 		
import os 			  		 			 	 	 		 	
from util import get_data, plot_data 			  		 			 	 	
 			  		 			 	 	 		 		
def compute_portvals(orders_file = "./orders/orders-01.csv", start_val = 1000000, commission=9.95, impact=0.005): 	
    orders_df=orders_file
    orders_df.sort_index(inplace=True)
    orders_impact=orders_df.copy()
    orders_df['Changes']=orders_df['Order']*orders_df['Shares']
    orders_impact['Order']=orders_impact['Order']+impact
    orders_impact['Changes']=orders_impact['Order']*orders_impact['Shares']
    orders_impact['Commissions']=commission
    orders_impact['Commissions'][orders_df['Order']==0]=0


    start_date=orders_df.index.values[0]
    end_date=orders_df.index.values[-1]
    labels=list(orders_df.Symbol.unique())


    prices=get_data(labels,pd.date_range(start_date,end_date),addSPY=False)
    prices['SPY']=get_data(['SPY'],pd.date_range(start_date,end_date),addSPY=False)
    prices['Cash']=np.ones(prices.shape[0])
    trades=prices.copy()
    trades.iloc[:,:]=0.0
    trades_modified=trades.copy()

    #Build the trades df. Can this process be vectorized though
    for row in orders_df.itertuples():
        row_dict=row._asdict()
        trades.loc[row_dict['Index'],row_dict['Symbol']]+=row_dict['Changes']

    for row in orders_impact.itertuples():
        row_dict=row._asdict()
        trades_modified.loc[row_dict['Index'],row_dict['Symbol']]+=row_dict['Changes']


    #NOTE: Below is the solution for market impact
    commission=orders_impact['Commissions'].groupby(orders_impact.index.values).sum()
    trades['Cash']= -(trades_modified*prices).sum(axis=1)-commission
    #NOTE:DEBUG#####################
    #print trades[14:25]
    #exit()
    #NOTE:DEBUG#####################
    #NOTE: Not sure if this will work
    trades.fillna(0.0,inplace=True)

    #Set the non-trading days' trade rows to NaN
    trades[pd.isnull(prices['SPY'])]=np.nan
    #Build Holdings df
    holdings=prices.copy()
    holdings.iloc[:,:]=0.0
    holdings['Cash']=start_val
    holdings=holdings+trades.cumsum()
    #Build values df
    values=prices.copy()
    values.iloc[:,:]=0.0
    values=holdings*prices
    portvals=values.sum(axis=1)
    portvals.fillna(method='ffill',inplace=True)
    portvals.fillna(method='bfill',inplace=True)

    


    return portvals  	
 		   
def author():
    return 'gyan31'

def test_code(): 			  		
    pass
if __name__ == "__main__":
    compute_portvals()
