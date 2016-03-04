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
<h1> Word Co-occurence analysis </h1>

<h4> Please select the newspaper(s) you wish to analyze below </h4>
<form action="cooc_get.py" method="get" target="_blank">
<input type="checkbox" name="NRC" value="on" /> NRC <br> 
<input type="checkbox" name="De Volkskrant" value="on" /> De Volkskrant<br>
Most popular X words [Between 1 and 100]: <input type="number" name="mostpop", max="10000">  <br>
Minimum amount of co-occurences [Between 1 and 3000]: <input type="number" name="maxcooc", min="1", max="3000"/><br>
Subset [Fill in the wanted value without deleting the beginning of the below example. You can add more arguments if needed e.g. "source":"nrc" "author":"Alan Smith"]:<br> <textarea name="usersubset" cols="40" rows="4">{$or: [{'source':'adnl'} </textarea><br>
<input type="submit" value="Submit fields" />
</form>
</body>
</html>
''')
