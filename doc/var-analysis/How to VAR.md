# Vector AutoRegression model
This guide provides general structure on how to work with multiple time-series models using VAR. Lets see what functionality there is available and how it works.

## Funcionality 
 1. Fit method:
	- Exexute a query to elasticsearch and generates a data frame with timeline ( calls: timeline_analysis )
		. might want to specify time period [from_time, to_time], default = everything/from all time history
		. See time_line method to see what queries you can create  
	- Checks whether the data is stationarity ( calls: test_assumptions ) 
	- If not stationary: differencing or detreding is performed ( calls: test_assumptions )
 	- Statsmodels fit method is applied to (stationary) dataframe ( calls: var.fit from statsmdoles) 
		 . # of lags defined by AIC [Default] 
 	- Perfomrs diagnostics: whiteness of the residuals, can do autoccorelation plot  ( calls: diagnostics ) 
 
 2. Test_assumptions method: 
	Confidence level = 5% [Default] 
 	- ADF test ( test for stationarity ) [Default] 
		Resource: https://en.wikipedia.org/wiki/Augmented_Dickey%E2%80%93Fuller_test 
	- KPSS test ( test for stationarity )
		Resource: http://www.statisticshowto.com/kpss-test/
	- Differencing ( d_y(t) = y(t) - y(t-m) ) 
		Resource: https://www.otexts.org/fpp/8/1
	- Detrending ( take residuals after regressing time/trend in the series ) 
		Resource: http://www.statsmodels.org/dev/generated/statsmodels.tsa.tsatools.detrend.html
			  http://desktop.arcgis.com/en/arcmap/latest/extensions/geostatistical-analyst/understanding-how-to-remove-trends-from-the-data.htm

 
 3. Diagnostics method: 
	- serial/autocorrelation of the residuals check via Ljung_Box test =  are residuals white noise ?
 	  	Resource: https://en.wikipedia.org/wiki/Ljung%E2%80%93Box_test
	- Plot autocorrelation function of residuals
 
 4. Granger method: 
 	- tetst whether one time series does not granger cause some other time series 
		Resource: http://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.grangercausalitytests.html

 4. Plotting method: 
	- Lag scatter plot. Scatter plot: Lag plots are used to check if a data set or time series is random. Random data 
            should not exhibit any structure in the lag plot. Non-random structure implies that the underlying 
            data are not random.
		Resource: https://pandas.pydata.org/pandas-docs/stable/visualization.html#visualization-lag 
	- Line plot
	- Autocorrelation plot.Autocorrelation plots are often used for checking randomness in time series.  
		Resource :  https://pandas.pydata.org/pandas-docs/stable/visualization.html#visualization-autocorrelation
 
 5. Interpretation method: 
	- summary table for var.fit 
	- pre-processing steps: e.g. differencing 
	- number of lags used in the fitted var model
 
 6. Quality method:
	- whiteness of residauls ( calls: diagnostics ) 
	- R2 of the model 
  
## VAR User Case 
To get a better idea, we are going to consider an example case of using VARs. Say, we want to see the time dynamics of query 1 ='finacial' , quary 2 = 'crisis'  
 
1) Import the module, create an instance of VAR   

```python
import inca
fin_model = inca.analysis.var_tsa_analysis.VAR()

```

2) Do the first 'fit'. For exmaple, we want to inspect the counts of all articles in our ElasticSearch INCA index which refer to: query_1 = "financial" , query_2 = "crisis" 


```python
fin_model.fit(queries=['economie','crisis'], timefield = 'publication_date', granularity = 'day',ic='bic')

```
Possible parameters to change ( not exhaustive list ) :

@queries  = what do you want to query from ES ? eg queries = ['Trump','Hillary']
 
@timefield = what field do you want to use to get the dates/timeline from ? 'META.ADDED'

@granularity = 'day'/'week'/'month' etc 

@nlags -  number of lags to consider, if none - rely on statsmodels to choose lag for you 

kwargs:        
 @level = confidence level for all your test (!) , default = 5%
 
 @from_time - beginning time 
 
 @to_time - end time, eg [01-12-2017] 
 
 @max_order_diff = maximum order of differencing, default = 2  
 
 @max_order_detrend = maximum order of detredning, default = 2
 
 @stationarity_kpss = True/False, False is default, hence you do ADF test
 
 @self.ic = aic/bic/fpe, information criteria, default ='aic'

+some parameters in timeline_analysis
 
3) See and interpret the results: 

```python
fin_model.diagnostics()
fin_model.plot('lag') # no significant pattern there => niiice 
fin_model.interpretation()
fin_model.quality() 

```
4) see if your model makes sense, refit if you want to try something else 


## For those brave enough:

consider resources which will make you even more familier with times series var models: 
- http://cadmus.eui.eu/handle/1814/19354
- http://apps.eui.eu/Personal/Canova/Articles/ch4.pdf
- https://www.google.nl/url?sa=t&rct=j&q=&esrc=s&source=web&cd=3&cad=rja&uact=8&ved=0ahUKEwi1puCR2KXYAhWMKFAKHc3rBOwQFgg-MAI&url=https%3A%2F%2Fwww.researchgate.net%2Ffile.PostFileLoader.html%3Fid%3D563d2dbe6225ff39e98b4567%26assetKey%3DAS%253A292924211384321%25401446849982801&usg=AOvVaw0zIYrIXDY0x6gEfgMjrOSw







