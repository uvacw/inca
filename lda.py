#!/usr/bin/env python3
# This is the wordcount file
import cgitb
import cgi
cgitb.enable()
print('Content-Type: text/html')
print('''

<html>

<head>
<title>(C) ASCOR University of Amsterdam</title>
<link rel=StyleSheet href="../defaultstyle.css" type="text/css">
</head>

<body>

<h1>Latent Dirichlet Allocation</h1>


<a class='Homelink' href='homepage.py'>Back to Homepage</a>

<h4> Please select the newspaper(s) you wish to analyze below </h4>
<form action="/cgi-bin/lda_get.py" method="get" target="_blank">
<ul>
<form action="cooc_get.py" method="get" target="_blank">
<input type="checkbox" name="nrc (www)" value="on" /> NRC (online)<br> 
<input type="checkbox" name="nrc (print)" value="on" /> NRC (print)<br> 
<input type="checkbox" name="volkskrant (www)" value="on" /> De Volkskrant (online)<br>
<input type="checkbox" name="volkskrant (print)" value="on" /> De Volkskrant (print)<br> 
<input type="checkbox" name="trouw (www)" value="on" /> Trouw (online)<br>
<input type="checkbox" name="trouw (print)" value="on" /> Trouw (print)<br> 
<input type="checkbox" name="fok" value="on" /> fok.nl<br> 
<input type="checkbox" name="geenstijl" value="on" /> geenstijl.nl<br> 
<input type="checkbox" name="metro (www)" value="on" /> Metro (online)<br>
<input type="checkbox" name="metro (print)" value="on" /> Metro (print)<br> 
<input type="checkbox" name="nu" value="on" /> nu.nl<br> 
<input type="checkbox" name="telegraaf (www)" value="on" /> Telegraaf (online)<br>
<input type="checkbox" name="telegraaf (print)" value="on" /> Telegraaf (print)<br> 
<input type="checkbox" name="ad (www)" value="on" /> Algemeen Dagblad (online)<br>
<input type="checkbox" name="ad (print)" value="on" /> Algemeen Dagblad (print)<br> 
<input type="checkbox" name="fd (print)" value="on" /> Financieele dagblad (print)<br> 
<input type="checkbox" name="spits (www)" value="on" /> Spits<br>
<input type="checkbox" name="parool (www)" value="on" /> Het Parool<br>
<input type="checkbox" name="sargasso" value="on" /> Sargasso<br>
<input type="checkbox" name="tpo" value="on" /> Tpo.nl<br>
<input type="checkbox" name="nos (www)" value="on" /> NOS<br>
<input type="checkbox" name="fok" value="on" /> Fok<br>
<input type="checkbox" name="anp" value="on" /> ANP<br>
</ul>
<br>

<h3> Please select the general criteria </h3>
<h4> Choose whether you want to work with whole articles or cleaned ones <br> (<i>Clean articles consist only of nouns, adjectives and adverbs. Stopwords have also been removed</i>):</h4>
<input type='checkbox' name='clean' value="on" /> Use cleaned articles <br>
<h4> Please select the date range that you are interested in below:</h4> 
<h5> Select the start date:</h5> 
Year [1995-2016]: <input type='number' name='year_start' max='2016' min='1995'>
Month [1-12]: <input type='number' name='month_start' max='12' min='1'>
Day [1-31]: <input type='number' name='day_start' max='31' min='1'>
<h5> Select the end date:</h5> 
Year [1995-2016]: <input type='number' name='year_end' max='2016' min='1995'>
Month [1-12]: <input type='number' name='month_end' max='12' min='1'>
Day [1-31]: <input type='number' name='day_end' max='31' min='1'>

<br><br>

<h3> Please select the LDA specific criteria below:</h3> 

<h4> Select the amount of topics you wish to retrieve from the sample </h4>
Choose a relevant number between 5 and 200
Topics to be retrieved: <input type='number' name='numtopics' max='200' min='5'>

<h4> Select the minimum word frequency you wish to use to filter topics from the sample </h4>
Choose the minimum frequency
Minimum word frequency: <input type='number' name='minfreq' max='100000' min='5'>

<br><br>

<h4> Additional segmentation </h4>
Subset [Fill in the wanted value without deleting the beginning of the below example. You can add more arguments if needed e.g. "source":"nrc" "author":"Alan Smith"]:<br> <textarea name="usersubset" cols="150" rows="4"> </textarea><br>
<br>

<input type="submit" value="Submit" />
</form>
</body>
</html>
''')

