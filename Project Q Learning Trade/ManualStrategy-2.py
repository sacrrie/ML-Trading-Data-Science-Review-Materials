"""
ML4T Summer 2019 Project 6: Manual Strategy

GTID:gyan31
GT Number:903272167

"""
import pandas as pd
import numpy as np
import datetime as dt
import marketsimcode as sim
import matplotlib.pyplot as plt
from indicators import indicators 
import os
from util import *

def testPolicy(symbol='JPM',sd=dt.datetime(2010,1,1),ed=dt.datetime(2010,1,1),sv=100000):
    #output column name should be Shares
    dates=pd.date_range(sd,ed)
    prices=get_data([symbol],dates,addSPY=False)
    prices['SPY']=get_data(['SPY'],dates,addSPY=False)
    SPY=prices['SPY'].to_frame()
    prices=prices.drop(['SPY'],axis=1)
    #prices.fillna(method='ffill',inplace=True)
    #prices.fillna(method='bfill',inplace=True)
    TSI,_,bbp,priceSMA=indicators(prices)
    TSI_SPY,_,_,_=indicators(SPY)

    #NOTE: the variable name 'forcasts' is from reused codes
    forcasts=prices['JPM'].copy()
    forcasts=forcasts.to_frame()
    forcasts['JPM']=0
    #forcasts[(priceSMA<0.95) & (bbp<0) & (TSI<-25) & (TSI_SPY>-25)]=1
    #forcasts[(priceSMA>1.05) & (bbp>1) & (TSI>25) &  (TSI_SPY< 25)]=-1
    #forcasts[ (TSI<-25) & (TSI_SPY>-25) ]=1
    #forcasts[ (TSI> 20) & (TSI_SPY< 20) ]=-1
    #forcasts[(priceSMA<0.95) & (TSI<-25) & (TSI_SPY>-25)]=1
    #forcasts[(priceSMA>1.00) & (TSI> 20) & (TSI_SPY< 20)]=-1
    forcasts[(priceSMA<0.95)  & (TSI_SPY>-25)]=1
    forcasts[(priceSMA>1.00)  & (TSI_SPY< 20)]=-1
    #eliminate states on non-trading days
    #TODO: check if this line below works
    #forcasts[pd.isnull(SPY['SPY'])]=0
    temp=forcasts.copy()
    temp['SPY']=get_data(['SPY'],dates,addSPY=False)
    forcasts[pd.isnull(temp['SPY'])]=0
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

    results=forcasts['Shares']
    results=results.to_frame()
    return results

def author():
    return 'gyan31'

def transform(data):
    data['Symbol']='JPM'
    data['Order']=np.sign(data['Shares'])
    data['Shares']=abs(data['Shares'])
    return data

def test_manual(symbol,sd,ed,opening,title=''):
    syb=symbol
    start=sd
    end=ed
    openings=opening
    temp=get_data(['JPM'],pd.date_range(start,end),addSPY=False)
    manuals=testPolicy('JPM',start,end)
    benchmark=manuals.copy()
    ###TODO###
    #print benchmark
    ###TODO###
    benchmark.iloc[:,:]=0.0
    benchmark=transform(benchmark)
    manuals=transform(manuals)
    benchmark.loc[temp['JPM'].first_valid_index(),'Shares']=1000
    benchmark.loc[temp['JPM'].first_valid_index(),'Order']=1
    #NOTE:making an temporary transformation to accomadate marketsim
    result=sim.compute_portvals(manuals,start_val=openings,commission=9.95,impact=0.005)
    ###############NOTE:DEBUG NOTE#################
    #print manuals[manuals['Order']<0]
    #print result
    #exit()
    ###############NOTE:DEBUG NOTE#################
    #change the column name for optimal
    result=result.to_frame()
    result.columns=['manual']
    result['benchmark']=sim.compute_portvals(benchmark,start_val=openings,commission=9.95,impact=0.005)
    result=result.div(result.iloc[0],axis=1)
    result.fillna(method='ffill',inplace=True)
    result.fillna(method='bfill',inplace=True)
    ax=result.plot(title="Manual Strategy and Benchmark",style=['r','g'])
    longs=result.index[manuals['Order']==1].tolist()
    shorts=result.index[manuals['Order']==-1].tolist()
    for xl in longs:
        ax.axvline(x=xl, color='b', linestyle='-')
    for xs in shorts:
        ax.axvline(x=xs, color='k', linestyle='-')
    plt.savefig(title+"manual_benchmark.png")
    plt.clf()
    dr_op=result['manual'][1:]/result['manual'][:-1].values - 1
    dr_op[0]=0
    dr_base=result['benchmark'][1:]/result['benchmark'][:-1].values - 1
    dr_base[0]=0
    adr_op=dr_op.mean()
    adr_base=dr_base.mean()
    sddr_op=dr_op.std()
    sddr_base=dr_base.std()
    cr_op=result['manual'][-1]-1
    cr_base=result['benchmark'][-1]-1
    print "cumulative return, mean,std of daily returns of Manual is"
    print cr_op,adr_op,sddr_op
    print "cumulative return, mean,std of daily returns of Benchmark is"
    print cr_base,adr_base,sddr_base

if __name__=="__main__":
    test_manual('JPM',dt.datetime(2008,1,1),dt.datetime(2009,12,31),100000)
    print 'Part 4'
    test_manual('JPM',dt.datetime(2010,1,1),dt.datetime(2011,12,31),100000,title='part4')
    
