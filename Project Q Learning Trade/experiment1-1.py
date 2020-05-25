"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
 			  		 			 	 	 		 		 	  		   	  			  	
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
Student Name: YAN, Guanyu (replace with your name)
GT User ID: gyan31 (replace with your User ID)
GT ID: 903272167 (replace with your GT ID)
"""
import datetime as dt
import pandas as pd
from ManualStrategy import *
from StrategyLearner import StrategyLearner as sl

import marketsimcode as sim
import matplotlib.pyplot as plt

def author():
    return 'gyan31'
    
def test(symbol,sd,ed,sv):
    Ql=sl(impact=0.005)
    syb=symbol
    start=sd
    end=ed
    openings=sv
    temp=get_data(['JPM'],pd.date_range(start,end),addSPY=False)
    print "Learner training...."
    Ql.addEvidence('JPM')
    print "Traning Complete"
    manuals=Ql.testPolicy(syb,start,end)
    temp['Shares']=manuals
    manuals=temp[['Shares',]]
    benchmark=manuals.copy()
    benchmark.iloc[:,:]=0.0
    benchmark=transform(benchmark)
    manuals=transform(manuals)
    benchmark.loc[temp['JPM'].first_valid_index(),'Shares']=1000
    benchmark.loc[temp['JPM'].first_valid_index(),'Order']=1
    #NOTE:making an temporary transformation to accomadate marketsim
    #NOTE:How about the commission in this case?
    result=sim.compute_portvals(manuals,start_val=openings,commission=9.95,impact=0.005)
    #change the column name for optimal
    result=result.to_frame()
    result.columns=['Q_learning']
    result['benchmark']=sim.compute_portvals(benchmark,start_val=openings,commission=9.95,impact=0.005)
    result=result.div(result.iloc[0],axis=1)
    result.fillna(method='ffill',inplace=True)
    result.fillna(method='bfill',inplace=True)
    ax=result.plot(title="Q Learning Strategy and Benchmark",style=['r','g'])
    longs=result.index[manuals['Order']==1].tolist()
    shorts=result.index[manuals['Order']==-1].tolist()
    for xl in longs:
        ax.axvline(x=xl, color='b', linestyle='-')
    for xs in shorts:
        ax.axvline(x=xs, color='k', linestyle='-')
    plt.savefig("QLearning_benchmark.png")
    plt.clf()
    dr_op=result['Q_learning'][1:]/result['Q_learning'][:-1].values - 1
    dr_op[0]=0
    dr_base=result['benchmark'][1:]/result['benchmark'][:-1].values - 1
    dr_base[0]=0
    adr_op=dr_op.mean()
    adr_base=dr_base.mean()
    sddr_op=dr_op.std()
    sddr_base=dr_base.std()
    cr_op=result['Q_learning'][-1]-1
    cr_base=result['benchmark'][-1]-1
    print "cumulative return, mean,std of daily returns of Q Learning is"
    print cr_op,adr_op,sddr_op
    print "cumulative return, mean,std of daily returns of Benchmark is"
    print cr_base,adr_base,sddr_base


if __name__=="__main__":
    test_manual('JPM',dt.datetime(2008,1,1),dt.datetime(2009,12,31),100000)
    test('JPM',dt.datetime(2008,1,1),dt.datetime(2009,12,31),100000)
    ###############NOTE:DEBUG NOTE#################
    #print manuals[manuals['Order']<0]
    #print result
    #exit()
    ###############NOTE:DEBUG NOTE#################
