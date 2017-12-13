import pandas as pd
import numpy as np
import logging 
from core.analysis_base_class import Analysis
from analysis import timeline_analysis as ta
from statsmodels.tsa.api import VAR as var 
from statsmodels.tsa.stattools import adfuller,kpss
from statsmodels.tsa.tsatools import detrend
from matplotlib import pyplot
from pandas.plotting import lag_plot
from statsmodels.graphics.tsaplots import plot_acf


logger = logging.getLogger(__name__)


class VAR(Analysis):
    """ When creating var model we first generate a timeline in the form of pandas df. Then feed it to VAR method in statsmodels.
        We can save the names of the variables(queries) this way so no need of mapping (var to name) on the later stages,
        awesome plotting functionality and just comfortable to work with for everyone. 
    """
     
    def __init__(self):  
        """creates variables: 
            @self.flag_stationarity = boolean of whether assumptions checks for VAR were run ## delete?!
        """
        
        self.flag_stationarity = False
        logger.warning("just  init some varaibles")    ##
        
    
    def fit(self,queries,timefield,granularity,querytype="count",nlags=None, **kwargs):
        """ @queries  = what do you want to query from ES ? eg queries = ['de','het']
            @timefield = what field do you want to use to get the dates/timeline from ? 'META.ADDED'
            @granularity = 'day'/'week'/'month' etc 
            @nlags -  number of lags to consider, if none - rely on statsmodels to choose lag for you
            
            Possible kwargs to be added later: 
                @do_assump_check = True/False
                @do_transfomations = True/False
                @max_order_diff = maximum order of differencing 
                @max_order_detrend = maximum order of detredning
        """
        timeline = ta.timeline_generator()
        df_raw = timeline.analyse(queries=queries,timefield = timefield, granularity = granularity)
        df_raw.index = df_raw.timestamp
        df_raw = df_raw.drop('timestamp',axis=1) 
        self.df_raw = df_raw
        ##self.model = var(self.df)     ## this makes a VAR model
        ## df = self.df  ## current dataframe that you are working with
    
        logger.warning("Before fitting, I automatically do assumptions' checks and modification to the model") 
        self.max_order_diff = 2
        self.max_order_detrend = 2
        
        self.check = self.test_assumptions(df_raw,level='1%')  ##  
        
        
        self.model = var(self.df)
        self.result = self.model.fit(nlags) 
        
        return ##

    def test_assumptions(self,df,level = '5%', **kwargs):
        """ 
        Gives you output as list with assumptions stated as satisfied/not satisfied. If some important 
        assumptions are not satisfied gives you warning that you have to transform your data. 
        
        @df - 'active' df which we might wnat to modify
        @level -  this is the level you are testing your asusmptions on (either 1,5 or 10 %)
        """
        self.level =  level
        
        def _adf_test(df):
            """ 
            H_0: the observed time series is stationary 
            Returns: dataframe of summary of the test 
            """
            summary_adf = pd.DataFrame(columns=['ADF_Stat','p-value','Critical_val_1%','Critical_val_5%','Critical_val_10%'])
            for name in df.columns:
                series = df[name]
                result = adfuller(series)
                dic = {'ADF_Stat':result[0],'p-value':result[1],'Critical_val_1%':result[4]['1%'],'Critical_val_5%':result[4]['5%'],
                       'Critical_val_10%':result[4]['10%']}
                summary_adf = summary_adf.append(dic,ignore_index=True)
            summary_adf.set_index(df.columns,inplace=True)  

            return summary_adf 
    
        
        def _stationary(df, explicit=True):
            """ 
            For each time series return the result of the check - return in created dataframe ?
            """
            lvl = float(self.level[:-1])/100 
            self.summary_adf = _adf_test(df)
            stat_flag = True       ## if test failed, we assume we need to take action 
            if explicit:
                for i in df.columns:
                    adf_flag = lvl > self.summary_adf.loc[i,'p-value']
                    if (adf_flag == False):
                        stat_flag = False 
                    print("For {} stationarity is satisfied: ADF - {}".format(i,adf_flag)) ## PRINT (!)
                    
            return stat_flag 
        
        def differencing(df, order=1):
            """ If there is no stationarity: try differencing
            """  
            helped = False   ## boolean check if differencing helped 
            def _perform_differencing():
            # Perform differencing:  
                df_diff = pd.DataFrame(columns=df.columns)
                for name in df.columns:
                    series = df[name]
                    series = series.diff(order)
                    df_diff[name] = series.dropna(axis=0)
                
                return _stationary(df_diff),df_diff   
            
            stat_check_after_diff, df_diff = _perform_differencing()
            print('Differencing helped?')   ##            
            print(stat_check_after_diff)   ##
            
            ## if differencing helped update self.df => self.df = df_diff 
            if stat_check_after_diff == True: 
                self.df = df_diff       ## CREATING FINAL DF for the first time if differncing helped
                helped = True   
                
            return helped
        
        def detrending(df, order=1):
            """ If there is no stationarity: differencing did not help - detrend
            
                (!) does not work nicely with time series where there is a lot of zeros and high volatility :(
            """     
            helped = False  ## boolean check if detrending helped
            def _perform_detrending():
            # Perform detrending:  
                df_res = pd.DataFrame(columns=df.columns)
                for name in df.columns:
                    series = df[name]
                    res = detrend(series,order)
                    df_res[name] = series.dropna(axis=0)
                
                return _stationary(df_res), df_res  
            
            stat_check_after_detrend,df_detrended = _perform_detrending()
            print('Detrending helped?')       ##            
            print(stat_check_after_detrend)   ##
            
            ## if detrending helped update self.df => self.df = df_diff 
            if stat_check_after_detrend == True: 
                self.df = df_detrended             ## CREATING FINAL DF for the first time if detrending helped
                helped = True   
            
            return helped
        
        
        self.flag_stationarity = _stationary(df,explicit=False)
        
        if self.flag_stationarity == True: 
            self.df = self.df_raw               ## if no transoformation needed - just use df_raw
            print('No need in transforms as stationarity is {}'.format(self.flag_stationarity))
        else: 
            # (1) start the iterative procedure of differencing
            for i in range(1,self.max_order_diff + 1):
                diff_helped = differencing(df,order=i)
                if diff_helped == True:
                    print(self.df)
                    self.flag_stationarity = diff_helped 
                    break 
            # (2) if differencing did not help do detrending 
            if self.flag_stationarity == False: 
                for i in range(1,self.max_order_detrend + 1):
                    detrend_helped = detrending(df,order=i)
                    if detrend_helped == True:
                        print(self.df)
                        self.flag_stationarity = detrend_helped 
                        break
            
        return ##