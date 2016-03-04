#!/usr/bin/env python3
# This is the cooc file
import cgitb
import cgi
cgitb.enable()
print('Content-Type: text/html')
print('''
<html>
<head>
<a href='homepage.py'>Back to Homepage</a>
</head>
<body>
<h1> Sentiment Analysis</h1>

<h4> Please select the newspaper(s) you wish to analyze below </h4>
<form action="cooc_get.py" method="get" target="_blank">
<input type="checkbox" name="NRC" value="on" /> NRC <br> 
<input type="checkbox" name="De Volkskrant" value="on" /> De Volkskrant<br>
Most popular X words [Between 1 and 100]: <input type="number" name="mostpop", max="100">  <br>
Minimum amount of co-occurences [Between 1 and 3000]: <input type="number" name="maxcooc", min="1", max="3000"/><br>
<input type="submit" value="Submit fields" />
</form>)

</body>
</html>
''')

