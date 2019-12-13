import pandas as pd
import numpy as np
import logging
from os import environ
from ..core.analysis_base_class import Analysis
from . import timeline_analysis as ta
from statsmodels.tsa.api import VAR as var
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.tsatools import detrend
from pandas.plotting import lag_plot
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import grangercausalitytests
from sklearn.metrics import r2_score

logger = logging.getLogger("INCA")

if "DISPLAY" in environ:
    from matplotlib import pyplot
else:
    logger.warning(
        "$DISPLAY environment variable is not set, trying a different approach. You probably are running INCA on a text console, right?"
    )
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot


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

    def fit(
        self, queries, timefield, granularity, querytype="count", nlags=None, **kwargs
    ):
        """ @queries  = what do you want to query from ES ? eg queries = ['Trump','Hillary']
            @timefield = what field do you want to use to get the dates/timeline from ? 'META.ADDED'
            @granularity = 'day'/'week'/'month' etc 
            @nlags -  number of lags to consider, if none - rely on statsmodels to choose lag for you 
            
            Possible kwargs to be added later:
                @level = confidence level for all your test (!) , default = 5%
                @from_time - 
                @to_time -
                @do_assump_check = True/False    ##
                @do_transfomations = True/False   ##
                @max_order_diff = maximum order of differencing, default = 2  
                @max_order_detrend = maximum order of detredning, default = 2
                @stationarity_kpss = True/False, False is default, hence you do ADF test
                @self.ic = aic/bic/fpe, information criteria, default ='aic'
        """
        self.max_order_diff = kwargs.get("max_order_diff", 2)
        self.max_order_detrend = kwargs.get("max_order_detrend", 2)
        self.stationarity_kpss = kwargs.get("stationarity_kpss", False)
        self.level = kwargs.get("level", "5%")
        self.from_time = kwargs.get("from_time", None)
        self.to_time = kwargs.get("to_time", None)
        self.ic = kwargs.get("ic", "aic")

        timeline = ta.timeline_generator()
        df_raw = timeline.analyse(
            queries=queries,
            timefield=timefield,
            granularity=granularity,
            from_time=self.from_time,
            to_time=self.to_time,
        )
        df_raw.index = df_raw.timestamp
        df_raw = df_raw.drop("timestamp", axis=1)
        self.df_raw = df_raw

        # Do the stationarity modifications
        logger.warning("Before fitting, I automatically check stationarity assumption")
        check_1 = self.test_assumptions(df_raw)

        # Fit the VAR model
        if self.flag_stationarity == True:
            logger.warning("You are good to go")
        else:
            logger.warning("Be warned: some time series are still non-stationary")
        self.model = var(self.df)
        self.result = self.model.fit(nlags, ic=self.ic)

        # Lets do diagnostics:
        check_2 = self.diagnostics()

        return  # fit

    def test_assumptions(self, df, level="5%", **kwargs):
        """ This method checks if df_raw needs to be made stationary; if stationary this becomes df 
            which you then use for the fit method; if your raw df is not stationary then we do transfomations 
            such as differencing or detrending. 
                        
        @df - 'active' df which we might want to modify
        @level -  this is the level you are testing your asusmptions on. 
                  NOTE: when test_assump called from fit method level is set by kwarg or default is 5%
        @test_type - either adf or kpss
        """
        self.diff_order = 0
        self.detrend_order = 0

        def _adf_test(df):
            """ 
            H_0: the observed time series is stationary 
            Returns: dataframe of summary of the test 
            """
            summary_adf = pd.DataFrame(
                columns=[
                    "ADF_Stat",
                    "p-value",
                    "Critical_val_1%",
                    "Critical_val_5%",
                    "Critical_val_10%",
                ]
            )
            for name in df.columns:
                series = df[name]
                result = adfuller(series)
                dic = {
                    "ADF_Stat": result[0],
                    "p-value": result[1],
                    "Critical_val_1%": result[4]["1%"],
                    "Critical_val_5%": result[4]["5%"],
                    "Critical_val_10%": result[4]["10%"],
                }
                summary_adf = summary_adf.append(dic, ignore_index=True)
            summary_adf.set_index(df.columns, inplace=True)

            return summary_adf

        def _kpss_test(df):
            """ 
            H_0: there is a unit root in time series, hence stochastic trend with drift, hence non-stationary
            Returns: dataframe of summary of the test
            """
            summary_kpss = pd.DataFrame(
                columns=[
                    "KPSS_Stat",
                    "p-value",
                    "Critical_val_1%",
                    "Critical_val_5%",
                    "Critical_val_10%",
                ]
            )
            for name in df.columns:
                series = df[name]
                result = kpss(series)
                dic = {
                    "KPSS_Stat": result[0],
                    "p-value": result[1],
                    "Critical_val_1%": result[3]["1%"],
                    "Critical_val_5%": result[3]["5%"],
                    "Critical_val_10%": result[3]["10%"],
                }
                summary_kpss = summary_kpss.append(dic, ignore_index=True)
            summary_kpss.set_index(df.columns, inplace=True)

            return summary_kpss

        def _stationary(df):
            """ 
            For each time series return the result of the check - return in created dataframe ?
            Uses by default adf_ test, but if you want kpss test you have to give an argument
            """
            lvl = float(self.level[:-1]) / 100
            stat_flag = True
            if self.stationarity_kpss == False:
                self.summary_adf = _adf_test(df)
                for i in df.columns:
                    adf_flag = lvl > self.summary_adf.loc[i, "p-value"]
                    if adf_flag == False:
                        stat_flag = False
            else:
                self.summary_kpss = _kpss_test(df)
                for i in df.columns:
                    kpss_flag = lvl < self.summary_kpss.loc[i, "p-value"]
                    if kpss_flag == False:
                        stat_flag = False

            return stat_flag

        def differencing(df, order=1):
            """ If there is no stationarity: try differencing
            """
            helped = False

            def _perform_differencing():
                df_diff = pd.DataFrame(columns=df.columns)
                for name in df.columns:
                    series = df[name]
                    series = series.diff(order)
                    df_diff[name] = series.dropna(axis=0)

                return _stationary(df_diff), df_diff

            stat_check_after_diff, df_diff = _perform_differencing()

            if stat_check_after_diff == True:
                self.df = df_diff
                helped = True

            return helped

        def detrending(df, order=1):
            """ If there is no stationarity: differencing did not help - detrend
               (!) does not work nicely with time series where there is a lot of zeros and high volatility :(
            """
            helped = False

            def _perform_detrending():
                df_res = pd.DataFrame(columns=df.columns)
                for name in df.columns:
                    series = df[name]
                    res = detrend(series, order)
                    df_res[name] = series.dropna(axis=0)

                return _stationary(df_res), df_res

            stat_check_after_detrend, df_detrended = _perform_detrending()
            if stat_check_after_detrend == True:
                self.df = df_detrended
                helped = True

            return helped

        self.flag_stationarity = _stationary(df)

        if self.flag_stationarity == True:
            self.df = self.df_raw
        else:
            for i in range(1, self.max_order_diff + 1):
                self.diff_order = i
                diff_helped = differencing(df, order=i)
                if diff_helped == True:
                    self.flag_stationarity = diff_helped
                    break

            if self.flag_stationarity == False:
                for i in range(1, self.max_order_detrend + 1):
                    detrend_helped = detrending(df, order=i)
                    if detrend_helped == True:
                        self.flag_stationarity = detrend_helped
                        break
            if self.flag_stationarity == False:
                logger.warning(
                    "Differencing and detrending did not help. Fit is applied to non-stationary series"
                )
                self.df = self.df_raw

    def diagnostics(self, level="5%", **kwargs):

        """ Possible diagnostics: 
                1. serial/autocorrelation of the residuals check via Ljung_Box test
                2. residual acf plot 
            
            @level = what confidence level to use in test Ljung_Box. 
                     NOTE: when test_assump called from fit method level is set by kwarg or default is 5%
       
            Possible kwargs to be added later:
                @do_plot = boolean, show the acf plot of the residuals, default = False
        """
        residuals = self.result.resid
        do_plot = kwargs.get("do_plot", False)
        self.lag = int((len(self.result.params) - 1) / len(self.df.columns))

        def _ljbox_test():
            """H_0: the data are independently distributed, not enough evidence to supoprt serial corr
            Returns: dataframe of summary of the test 
            """
            summary_ljb = pd.DataFrame(columns=["ljbvalue", "p-value"])
            for name in self.df.columns:
                series = residuals[name]
                result = acorr_ljungbox(series, lags=self.lag)
                dic = {
                    "ljbvalue": result[0][self.lag - 1],
                    "p-value": result[1][self.lag - 1],
                }
                summary_ljb = summary_ljb.append(dic, ignore_index=True)
            self.summary_ljb = summary_ljb.set_index(self.df.columns)

            lvl = float(self.level[:-1]) / 100
            res_white_flag = True
            for i in self.df.columns:
                not_white = lvl > self.summary_ljb.loc[i, "p-value"]
                if not_white == True:
                    res_white_flag = False

            return res_white_flag

        def _plot_res_acf(do_plot):
            if do_plot:
                for name in self.df.columns:
                    series = residuals[name]
                    print("Residuals autocorelation plot for {}".format(name))
                    plot_acf(series, lags=self.lag)
                    pyplot.show()

        res_check = _ljbox_test()
        _plot_res_acf(do_plot)

        return res_check

    def granger(self, ts_1, ts_2, level, lag):
        """The Null hypothesis for grangercausalitytests is that the time series in the second column,
            x2, does NOT Granger cause the time series in the first column, x1.
            
            @ts_1 - time series which is assumed to not granger cause ts_2 (regressor)
            @ts_2 - time series which is assumed to be not granger cause ts_1 
            @level - confidence level of ssr f test 
            @lag - lag at which we want the test
        """
        array = self.df.iloc[:, [ts_2 - 1, ts_1 - 1]].values

        table = grangercausalitytests(array, maxlag=lag, verbose=False)[lag][0]
        self.granger_table = pd.DataFrame.from_dict(table, orient="index")
        old_names = list(self.granger_table.columns)
        new_names = ["F-val", "p-val", "df_denom", "df_num"]
        self.granger_table.rename(columns=dict(zip(old_names, new_names)), inplace=True)

        result = grangercausalitytests(array, maxlag=lag, verbose=False)[lag][0][
            "ssr_ftest"
        ]

        granger_flag = result[1] < float(level[:-1]) / 100

        return granger_flag  # for granger

    def plot(self, plot_type=None, lag=1):
        """ Ploting graphs for df """

        def lag_scatter():
            for name in self.df.columns:
                series = self.df[name]
                print("Lag plot where y is {}".format(name))
                lag_plot(series, lag)
                pyplot.show()

        def line_plot():
            for name in self.df.columns:
                series = self.df[name]
                series.plot(legend=True)
                pyplot.show()
            return  ##

        def autocorrelation_plot():
            for name in self.df.columns:
                series = self.df[name]
                print("Autocorelation plot for {}".format(name))
                plot_acf(series, lags=lag)
                pyplot.show()

        if plot_type == None:
            lag_scatter()
            line_plot()
            autocorrelation_plot()
        if plot_type == ("line"):
            line_plot()
        if plot_type == ("lag"):
            lag_scatter()
        if plot_type == ("autocorrelation"):
            autocorrelation_plot()

    def interpretation(self, **kwargs):
        """
        - Summary table
        - Data preprocessing: 
            - detrended_order
            - differenced_order 
        """
        print("Summary for VAR model")
        print(self.result.summary())
        print("Pre-processing perforemed:")
        print("1) Differencing of {} order".format(self.diff_order))
        print("2) Detrending of {} order".format(self.detrend_order))
        print("Model fit:")
        print("3) Number of lags {} ".format(self.lag))

    def quality(self, **kwargs):
        """
        - Outliers (??) - there will be no significant outliers with stationarity: outliers detection
          for stationary time-series is too advanced topic. 
        
        - white noise residuals - this is done by diagnostics so I call diagnostic here
        - (From me:) VAR lag order selection table fto see which lags could also be tried  
        - if R2 below some benchmark give a message 'proceed with caution' 
        """
        print(
            "1) Residuals of the model are White Noise: {} ".format(self.diagnostics())
        )

        predicted = self.df.values[: -self.lag, :] - self.result.resid.values
        true = self.df.values[: -self.lag, :]
        self.r2 = r2_score(true, predicted)
        print("2) R-squared is {} ".format(self.r2))
