#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable()

print('Content-Type: text/html')
print('''
<head>
<title>(C) ASCOR University of Amsterdam</title>
<link rel=StyleSheet href="../defaultstyle.css" type="text/css">
</head>

<body>
<ul class='header'>
<a class='Homelink' href='hello.py'>Home</a>
<h1 class='title'>Welcome on the ASCOR analysis website</h1>
<p><em>Please choose one of the options below to proceed</em></p> 
<li>	<a class='wordcount' href='wordcount.py'>Word counts</a></li>
<li>	<a class='sentiment' href='sentiment.py'>Sentiment analysis</a></li>
<li>
	<a class='co-occurence analysis' href='cooc.py'>Co-occurence analysis</a>
</li>
<li> <a class='analysis' href='pca.py'>Principal Component Analysis (PCA)</a> </li>
<h2> Contact the team </h2>
<a class='contact' href='mailto:d.c.trilling@uva.nl.com'> Send us an email </a>
</body>
''')

