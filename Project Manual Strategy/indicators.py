"""
ML4T Summer 2019 Project 6: Manual Strategy

GTID:gyan31
GT Number:903272167

"""
import pandas as pd
import numpy as np
import datetime as dt
import os
import matplotlib.pyplot as plt
from util import *

def indicators(data,plot=False):
    """
    prices as the input df.
    for the NaNs, we are fill it by ffill and bfill
    rolling window is 7 for a week basis observation
    return TSI, momentum, bbp, priceSMA
    """
    #should the data to be a df that includes opening prices?
    lookback=7
    data.fillna(method='ffill',inplace=True)
    data.fillna(method='bfill',inplace=True)
    symbl=data.columns.values[0]
    #data=inputs['closed']

    #price/SMA
    prices=data.copy()
    prices['SMA']=prices.rolling(window=lookback,min_periods=lookback,center=False).mean()
    prices.fillna(method='ffill',inplace=True)
    prices.fillna(method='bfill',inplace=True)
    prices=prices.div(prices.iloc[0],axis=1)
    #prices['Price/SMA']=prices['JPM']/prices['SMA']
    prices['Price/SMA']=prices[symbl]/prices['SMA']
    #for output
    priceSMA=prices['Price/SMA'].copy()
    if plot:
        prices.plot(title="Indicator: Price/SMA(Price and SMA normalized)")
        plt.savefig("indicator_p_sma.png")
        plt.clf()

    #Bollinger Bands %
    prices=data.copy()
    prices.fillna(method='ffill',inplace=True)
    prices.fillna(method='bfill',inplace=True)
    prices=prices.div(prices.iloc[0],axis=1)
    prices['SMA']=prices.rolling(window=lookback,min_periods=lookback,center=False).mean()
    #prices['SM_STD']=prices['JPM'].rolling(window=lookback,min_periods=lookback,center=False).std()
    prices['SM_STD']=prices[symbl].rolling(window=lookback,min_periods=lookback,center=False).std()
    prices['Upper Bound']=prices['SMA']+2*prices['SM_STD']
    prices['Lower Bound']=prices['SMA']-2*prices['SM_STD']
    prices['Bolinger Bands % Number']=(prices[symbl]-prices['Lower Bound'])/(prices['Upper Bound']-prices['Lower Bound'])
    #prices['Bolinger Bands % Number']=(prices['JPM']-prices['Lower Bound'])/(prices['Upper Bound']-prices['Lower Bound'])
    prices.fillna(method='ffill',inplace=True)
    prices.fillna(method='bfill',inplace=True)
    bbp=prices['Bolinger Bands % Number'].copy()
    if plot:
        prices.plot(title="Indicator: Bolinger Bands %(Price Normalized)")
        plt.savefig("indicator_bbp.png")
        plt.clf()

    #momentum
    prices=data.copy()
    prices.fillna(method='ffill',inplace=True)
    prices.fillna(method='bfill',inplace=True)
    prices=prices.div(prices.iloc[0],axis=1)
    shifts=prices.shift(periods=lookback)
    #prices['momentum']=prices/shifts.values-np.ones(prices.shape[0])
    prices['momentum']=prices/shifts.values-1
    prices.fillna(0,inplace=True)
    #prices.fillna(method='ffill',inplace=True)
    #prices.fillna(method='bfill',inplace=True)
    momentum=prices['momentum'].copy()
    if plot:
        prices.plot(title="Indicator: Momentum (Prices normalized)")
        plt.savefig("indicator_momentum.png")
        plt.clf()

   #True Strength Indicator
    prices=data.copy()
    #shifts=prices.shift(periods=1)
    prices['changes']=prices[1:]-prices[:-1].values
    prices['changes'][0]=0
    component1=prices['changes'].ewm(span=25,adjust=False).mean()
    component1=component1.ewm(span=13,adjust=False).mean()
    component2=abs(prices['changes']).ewm(span=25,adjust=False).mean()
    component2=component2.ewm(span=13,adjust=False).mean()
    prices['True Strength Indicator']=100*component1/component2
    prices.fillna(0,inplace=True)
    TSI=prices['True Strength Indicator'].copy()
    TSI[TSI==np.inf]=100
    prices['True Strength Indicator']=TSI
    if plot:
        prices['Upper Line']=25*np.ones(prices.shape[0])
        prices['Lower Line']=-25*np.ones(prices.shape[0])
        prices.fillna(method='ffill',inplace=True)
        prices.fillna(method='bfill',inplace=True)
        prices.plot(title="Indicator: True Strength Indicator")
        plt.savefig("indicator_TSI.png")
        plt.clf()
    #TODO:enough?
    #TSI=TSI.to_frame()
    #momentum=momentum.to_frame()
    #bbp=bbp.to_frame()
    #priceSMA=priceSMA.to_frame()
    return TSI, momentum, bbp, priceSMA

def author():
    return 'gyan31'

def test():
    start=dt.datetime(2008,1,1)
    end=dt.datetime(2009,12,31)
    data=get_data(['JPM'],pd.date_range(start,end),addSPY=False)
    indicators(data,plot=True)

if __name__=="__main__":
    test()




