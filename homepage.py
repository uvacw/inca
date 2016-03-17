#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable()
print('Content-Type: text/html')
print('''
<head>
(C) ASCOR University of Amsterdam
</head>

<body>
<ul class='header'>
<li class='topnav'>
	<a class='Homelink' href='hello.py'>Home</a>
	<h1 class='title'>Welcome on the ASCOR analysis website</h1>
</li>
<li>	<a class='wordcount' href='wordcount.py'>Word counts</a></li>
<li>	<a class='sentiment' href='sentiment.py'>Semtiment analysis</a></li>
<li>
	<a class='co-occurence analysis' href='cooc.py'>Co-occurence analysis</a>
</li>
<li> <a class='analysis' href='pca.py'>Principal Component Analysis (PCA)</a> </li>

<p>Please choose one of the options above to proceed</p> 
</body>
''')

