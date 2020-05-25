"""
ML4T Summer 2019 Project 6: Manual Strategy

GTID:gyan31
GT Number:903272167


"""
#TODO: Transforme the strategy to order file in project 5
import pandas as pd
import numpy as np
import datetime as dt
import marketsimcode as sim
import matplotlib.pyplot as plt
import os
from util import *

def testPolicy(symbol='JPM',sd=dt.datetime(2010,1,1),ed=dt.datetime(2010,1,1),sv=100000):
    #output column name should be Shares
    dates=pd.date_range(sd,ed)
    prices=get_data([symbol],dates,addSPY=False)
    forcasts=prices.shift(periods=-1).values-prices
    forcasts['JPM'][-1]=0
    ###############NOTE:DEBUG NOTE#################
    temp=forcasts.copy()
    temp['SPY']=get_data(['SPY'],dates,addSPY=False)
    forcasts[pd.isnull(temp['SPY'])]=0
    #print result.head()
    #exit()
    ###############NOTE:DEBUG NOTE#################

    forcasts['Shares']=np.zeros(prices.shape[0])
    current_share=0
    for row in forcasts.itertuples():
        row_dict=row._asdict()
        if row_dict['JPM']>0:
            if current_share==0:
                current_share+=1000
                forcasts.loc[row_dict['Index'],'Shares']=1000
            elif current_share<0:
                current_share+=2000
                forcasts.loc[row_dict['Index'],'Shares']=2000
        elif row_dict['JPM']<0:
            if current_share==0:
                current_share-=1000
                forcasts.loc[row_dict['Index'],'Shares']=-1000
            elif current_share>0:
                current_share-=2000
                forcasts.loc[row_dict['Index'],'Shares']=-2000
    results=forcasts.loc[:,'Shares']
    results=results.to_frame()
    #results.columns=[symbol]
    return results

def author():
    return 'gyan31'

def transform(data):
    #data.columns=['Shares']
    data['Symbol']='JPM'
    data['Order']=np.sign(data['Shares'])
    data['Shares']=abs(data['Shares'])
    return data

def test():
    syb='JPM'
    start=dt.datetime(2008,1,1)
    end=dt.datetime(2009,12,31)
    openings=100000
    temp=get_data(['JPM'],pd.date_range(start,end),addSPY=False)
    optimal=testPolicy('JPM',start,end)
    benchmark=optimal.copy()
    benchmark.iloc[:,:]=0.0
    benchmark.loc[temp['JPM'].first_valid_index(),'Shares']=1000
    benchmark.loc[temp['JPM'].first_valid_index(),'Order']=1
    #NOTE:making an temporary transformation to accomadate marketsim
    optimal=transform(optimal)
    benchmark=transform(benchmark)
    result=sim.compute_portvals(optimal,start_val=openings,commission=0.0,impact=0.0)
    result=result.to_frame()
    #change the column name for optimal
    result.columns=['optimal']
    result['benchmark']=sim.compute_portvals(benchmark,start_val=openings,commission=0.0,impact=0.0)
    result=result.div(result.iloc[0],axis=1)
    result.fillna(method='ffill',inplace=True)
    result.fillna(method='bfill',inplace=True)
    result.plot(title="Theorectical Optimal and Benchmark",style=['r','g'])
    plt.savefig("optimal_benchmark.png")
    plt.clf()
    dr_op=result['optimal'][1:]/result['optimal'][:-1].values - 1
    dr_op[0]=0
    dr_base=result['benchmark'][1:]/result['benchmark'][:-1].values - 1
    dr_base[0]=0
    adr_op=dr_op.mean()
    adr_base=dr_base.mean()
    sddr_op=dr_op.std()
    sddr_base=dr_base.std()
    cr_op=result['optimal'][-1]-1
    cr_base=result['benchmark'][-1]-1
    print "cumulative return, mean,std of daily returns of Optimal is"
    print cr_op,adr_op,sddr_op
    print "cumulative return, mean,std of daily returns of Benchmark is"
    print cr_base,adr_base,sddr_base

if __name__=="__main__":
    test()
