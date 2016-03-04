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
<h1>Word Counts</h1>



<h4> Please select the newspaper(s) you wish to analyze below </h4>
<form action="/cgi-bin/wordcount_get.py" method="get" target="_blank">

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
<br>

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

<h4> Amount of words to be retrieved: </h4>
Most popular X words [Between 1 and 100]: <input type="number" name="mostpop", max="10000">  <br><br>
<h4> Additional segmentation </h4>
Subset [Fill in the wanted value without deleting the beginning of the below example. You can add more arguments if needed e.g. "source":"nrc" "author":"Alan Smith"]:<br> <textarea name="usersubset" cols="40" rows="4"> </textarea><br>
<br>

<input type="submit" value="Submit" />
</form>
</body>
</html>
''')

