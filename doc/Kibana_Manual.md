
# Kibana Manual

In order to determine whether everything is running properly, we use visualizations that show us whether there are certain gaps that need to be filled in the web scrapers. For this we use Kibana. This manual will walk you through how to make the visualizations that are in the current Maintenance Dashboard yourself to get acquainted with creating visualizations and also how to use the Maintenance Dashboard to perform checkups.

## Create a line chart to check for gaps in the parsers - time-based

If you want to check whether a title, category, image, text etc. is missing for a number of articles in a certain time period it is useful to create a monthly overview in the form of a line chart. 

### Step 1: Create the line chart

- Go to 'Visualize' in side menu and click on the '+' icon next to the
  'Search' bar 
- Select 'Line' under 'Basic Charts' 
- Select 'inca'

### Step 2: Setting up the Y-Axis

- The Y-Axis can be found under 'metrics'
- Check whether Y-Axis' 'Aggregation' says 'Count' (this is often already set up)
- Change the label of the Y-Axis to 'Number of articles'

### Step 3: Setting up the X-Axis

- Click on 'X-Axis' under 'buckets'
- Choose 'Date Histogram' under 'Aggregation'
- Select 'publication_date' under 'Field'
- Under 'Interval' you can select what time interval you want to check the data. Advised is to not select 'Daily' as this can cause Kibana to shut down.
- Under 'Custom Label' you can put '(Time interval you chosen) interval'

### Step 4: Running and saving the graph

- To run the graph (also after edits you made to it) press the '>' button in the menu below 'inca'
- Save the graph by clicking 'Save' in the upper right corner

## Create a horizontal bar chart to check for gaps in the parsers - newspaper-based

If you want to check whether a title, category, image, text etc. is missing for a certain newspaper it is useful to create an overview in the shape of a horizontal bar plot. 

### Step 1: Create the bar plot

- Go to 'Visualize' in side menu and click on the '+' icon next to the
  'Search' bar 
- Select 'Horizontal Bar' under 'Basic Charts' 
- Select 'inca'

### Step 2: Setting up the Y-Axis

- The Y-Axis can be found under 'metrics'
- Check whether Y-Axis' 'Aggregation' says 'Count' (this is often already set up)
- Change the label of the Y-Axis to 'Number of articles'

### Step 3: Setting up the X-Axis

- Click on 'X-Axis' under 'buckets'
- Choose 'Terms' under 'Aggregation'
- Select 'doctype.keyword' under 'Field'
- Under 'Order By' choose 'Term'
- Under 'Custom Label' you can put 'Newspapers'

### Step 4: Running and saving the graph

- To run the graph (also after edits you made to it) press the '>' button in the menu below 'inca'
- Save the graph by clicking 'Save' in the upper right corner

## Create a dashboard that shows missing elements with your visualizations

Now you can put together a dashboard that contains your freshly made graphs. The point of a dashboard is putting multiple visualizations together. With a dashboard you can apply filters that will be adopted across the different visualizations and the graphs are interactive, which means that all visualizations will adhere to the information you retrieve from one of them. In the next section 'How to use the Maintenance Dashboard' will be explained how this interaction works.

- Go to 'Dashboard' in side menu and click on the '+' icon next to the
  'Search' bar 
- Select 'Add'
- Choose the visualizations you want to add
- If you scroll down you can see your dashboard and change the size and the placement of each visualization
- Click 'Save'
- Choose a title and description for the dashboard
- Click on the 'Save' button

## How to use the Maintenance Dashboard

The Maintenance Dashboard serves to check for gaps in the parsers by looking at what element is missing for what scraper in which time period. The Maintenance Dashboard consists of visualizations that let you easily display what is missing by applying filters to the visualizations. The Maintenance Dashboard can be found under 'Dashboard' in the side menu.

### Visualization 1: MD - What does not exist per doctype

The first visualization is a horizontal bar plot that can show for each newspaper what element(s) do not exist. This can be done by adding a filter:

- Click on 'Add a filter'
- Choose under 'Fields...' the element you want to check
- Choose under 'Operators...' the option 'does not exist'
- Under 'Label' you can put something like 'No (element you chosen)'
- Click 'Save'
- Want to remove a filter? Hover over the filter you want to delete and click on the trash bin.
- Want to disable the filter but not remove it? Hover over the filter you want to disable and click on the tick icon. Clicking on the empty tick box will enable the filter again.

The bar plot will now display how many articles miss the element you chosen for each newspaper. You probably also have noticed that the other visualizations in the dashboard also changed. The filter you have chosen applies to the entire dashboard so all visualizations adapt to each filter you set. Now we will look at the graph on the right that displays a timeline of articles published in a selected time period.

### Visualization 2: MD - Timeline of published articles

The second visualization is a line chart that shows on the X-Axis (un)filtered monthly time points and on the Y-Axis the number of articles published in this month. If you have selected a filter to check whether a certain element does not exist for certain articles, this line chart will show per month how many parsed articles are missing this element. By clicking on one time point or multiple (drag your cursor across the chart) in the graph you basically apply a time filter to the entire dashboard, which results into the other visualizations also adopting this filter. The filter also appears in the filter 'space' below the search bar. This way you can very easily see what newspapers miss a certain element in a specific month.

### Visualization 3: Aantal

This visualization is a very simple one that shows the number of articles with the applied filters. It might come in useful to see at a glance how many articles are selected or filtered. 
