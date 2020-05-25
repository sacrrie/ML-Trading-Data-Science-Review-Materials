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
import numpy as np
import pandas as pd
import util as ut
import random
from indicators import indicators 
import QLearner

class StrategyLearner(object):

    def __init__(self, verbose = False, impact=0.0):
        self.verbose = verbose
        self.impact = impact
        self.bin_list=[]
        self.learner=None

    # this method should create a QLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,12,31), \
        sv = 10000):
        syms=[symbol]
        dates = pd.date_range(sd, ed) 			  	     
        prices_all = ut.get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols 
        prices_SPY = prices_all[['SPY',]]  # only SPY, for comparison later
        if self.verbose: print prices
        
        #NOTE:Implementing Steps:
        #1. select & compute indicators(discretinize)
        TSI, momentum, _, priceSMA=indicators(prices)
        TSI_SPY, _, _, _=indicators(prices_SPY)
        #TSI, momentum, bbp, priceSMA=indicators(prices)

        #2. set up the learner
        #NOTE:0 do nothing, 1 long, 2 short, the exact number should beprocessed with additional works
        states_num,state_list=self.set_state([TSI_SPY,priceSMA])
        self.learner=QLearner.QLearner(num_states=states_num,num_actions=3)
        #3. LOOP Until cumulative return is no longer improving:
        #Converge criteria: Policy changes?Returns?DF differences?Runtime exceeds?
        policy=np.zeros(prices.shape[0])
        policy_changes=policy.shape[0]
        loop_num=40
        prices_SPY['label']=np.zeros(prices.shape[0])
        for i in range(len(state_list)):
            prices_SPY['label']+=state_list[i]*(10**(len(state_list)-i-1))

        while policy_changes>0.05*prices.shape[0] and loop_num>1:
            #Day 0 is:
            policy_temp=policy.copy()
            self.learner.a=0
            self.learner.s=int(prices_SPY['label'][0])
            holdings=0
            #4. for each day of the data:
            for i in range(1,prices.shape[0]):
                #1. Compute the current state
                state=int(prices_SPY['label'][i])
                #2. Compute the reward for last state
                rew=holdings*float(prices.iloc[i]-prices.iloc[i-1])
                #3. Train the learner with above data
                action=self.learner.query(state,rew)
                policy[i]=action
                #4. Implement the action the learner returned?
                if abs(holdings)<2000:
                    if action:
                        if action ==1 and holdings<1000:
                            holdings+=1000
                            prices=prices*(1+self.impact)
                        elif action ==2 and holdings>-1000:
                            holdings-=1000
                            prices=prices*(1-self.impact)
            #Calculate loop parameter changes
            loop_num-=1
            policy_change=policy[policy!=policy_temp].shape[0]



    def set_state(self,indicator_list):
        bins=10
        num_states=1
        lists=[]
        for i in indicator_list:
            a,bin_range=pd.qcut(i,bins,retbins=True,labels=False)
            lists.append(a)
            self.bin_list.append(bin_range)
            num_states*=bins
        return num_states,lists

    # this method should use the existing policy and test it against new data
    def get_actions(self,s):
        state=int(s)
        return self.learner.querysetstate(state)

    def testPolicy(self, symbol = "IBM", \
        sd=dt.datetime(2010,1,1), \
        ed=dt.datetime(2011,12,31), \
        sv = 10000):
        self.learner.rar=0
        # your code should return the same sort of data 
        dates = pd.date_range(sd, ed) 			
        prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
        trades = prices_all[[symbol,]]  # only portfolio symbols       
        trades_SPY = prices_all[['SPY',]]  # only SPY, for comparison later
        #1. Compute Current State
        TSI, momentum, _, priceSMA=indicators(trades)
        TSI_SPY, _, _, _=indicators(trades_SPY)
        indcts=[TSI_SPY,priceSMA]
        trades_SPY['label']=np.zeros(trades.shape[0])
        for i in range(len(indcts)):
            a=np.digitize(indcts[i],self.bin_list[i],right=True)-1
            a[a==-1]=0
            a[a==10]=9
            trades_SPY['label']+=a*(10**(len(indcts)-i-1))
        holdings=0
        trades=trades.replace(trades,0)
        #2. Querry the leanrer
        trades_SPY['actions']=trades_SPY['label'].apply(self.get_actions)
        for row in trades_SPY[['actions',]].itertuples():
            row_dict=row._asdict()
            #3. Execute the action reuturned and update the trades and portvals
            if row_dict['actions']==1:
                if holdings==0:
                    holdings+=1000
                    trades.loc[row_dict['Index'],symbol]=1000
                elif holdings<0:
                    holdings+=2000
                    trades.loc[row_dict['Index'],symbol]=2000
            elif row_dict['actions']==2:
                if holdings==0:
                    holdings-=1000
                    trades.loc[row_dict['Index'],symbol]=-1000
                elif holdings>0:
                    holdings-=2000
                    trades.loc[row_dict['Index'],symbol]=-2000

        return trades

    def author(self):
        return 'gyan31'


if __name__=="__main__":
    ql=StrategyLearner()
    ql.addEvidence(symbol="UNH")
    a=ql.testPolicy(symbol="UNH")
    print a.head()
        ####NOTE:DEBUG####
        #print self.learner.s
        #exit()
        ####NOTE:DEBUG####
