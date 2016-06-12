#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable()
form = cgi.FieldStorage()
from analysis import * 
from nvd3 import multiBarChart

# read config file and set up MongoDB

# GENERAL RULE:
# FIRST INCLUDE USER GENERATED QUERY + SOURCES + DATES.
# THIS WAY WE CAN ALWAYS CLOSE THE QUERY AFTER THE DATE ARGUMENT, WHETHER GIVEN OR NOT
if form.getvalue('usersubset'):
	usersubset =form.getvalue('usersubset')
	if usersubset == []:
		usersubset = "{'$or':["
	else:
		usersubset = "{'$or':[" + usersubset
else:
	usersubset = "{'$or':["

if form.getvalue('nrc (www)'):
	usersubset+=",{'source':'nrc (www)'}"
	nrc_www_flag = 'nrc (www)'
else:
	nrc_www_flag = ''

if form.getvalue('nrc (print)'):
	usersubset+=",{'source':'nrc (print)'}"
	nrc_print_flag = 'nrc (print)'
else:
	nrc_print_flag = ''

if form.getvalue('volkskrant (www)'):
	usersubset+=",{'source':'volkskrant (www)'}"
	volkskrant_www_flag= 'volkskrant (www)'
else:
	volkskrant_www_flag = ''

if form.getvalue('volkskrant (print)'):
	usersubset+=",{'source':'volkskrant (print)'}"
	volkskrant_print_flag= 'volkskrant (print)'
else:
	volkskrant_print_flag = ''

if form.getvalue('trouw (www)'):
	usersubset+=",{'source':'trouw (www)'}"
	trouw_www_flag= 'trouw (www)'
else:
	trouw_www_flag = ''

if form.getvalue('trouw (print)'):
	usersubset+=",{'source':'trouw (print)'}"
	trouw_print_flag= 'trouw (print)'
else:
	trouw_print_flag = ''

if form.getvalue('fok'):
	usersubset+=",{'source':'fok'}"
	fok_flag= 'fok'
else:
	fok_flag= ''

if form.getvalue('geenstijl'):
	usersubset+=",{'source':'geenstijl'}"
	geenstijl_flag= 'geenstijl'
else:
	geenstijl_flag= ''

if form.getvalue('metro (print)'):
	usersubset+=",{'source':'metro (print)'}"
	metro_print_flag= 'metro (print)'
else:
	metro_print_flag= ''

if form.getvalue('metro (www)'):
	usersubset+=",{'source':'metro (www)'}"
	metro_www_flag= 'metro (www)'
else:
	metro_www_flag= ''

if form.getvalue('nu'):
	usersubset += ",{'source':'nu'}"
	nu_flag = 'nu.nl'
else:
	nu_flag=''

if form.getvalue('telegraaf (print)'):
	usersubset += ",{'source':'telegraaf (print)'}"
	telegraaf_print_flag = 'telegraaf (print)'
else:
	telegraaf_print_flag = ''

if form.getvalue('telegraaf (www)'):
	usersubset += ",{'source':'telegraaf (www)'}"
	telegraaf_www_flag = 'telegraaf (www)'
else:
	telegraaf_www_flag = ''

if form.getvalue('ad (print)'):
	usersubset += ",{'source':'ad (print)'}"
	ad_print_flag = 'ad (print)'
else:
	ad_print_flag = ''

if form.getvalue('ad (www)'):
	usersubset += ",{'source':'ad (www)'}"
	ad_www_flag = 'ad (www)'
else:
	ad_www_flag = ''

if form.getvalue('fd (print)'):
	usersubset += ",{'source':'fd (print)'}"
	fd_print_flag = 'fd (print)'
else:
	fd_print_flag = ''

if form.getvalue('spits (www)'):
	usersubset += ",{'source':'spits (www)'}"
	spits_www_flag = 'spits (www)'
else:
	spits_www_flag = ''

if form.getvalue('parool (www)'):
	usersubset += ",{'source':'parool (www)'}"
	parool_www_flag = 'parool (www)'
else:
	parool_www_flag = ''

if form.getvalue('sargasso'):
	usersubset += ",{'source':'sargasso'}"
	sargasso_flag = 'sargasso'
else:
	sargasso_flag=''

if form.getvalue('tpo'):
	usersubset += ",{'source':'tpo'}"
	tpo_flag = 'tpo'
else:
	tpo_flag=''

if form.getvalue('nos (www)'):
	usersubset += ",{'source':'nos (www)'}"
	nos_www_flag = 'nos (www)'
else:
	nos_www_flag = ''

if form.getvalue('fok'):
	usersubset += ",{'source':'fok'}"
	fok_flag = 'fok'
else:
	fok_flag=''

if form.getvalue('anp'):
	usersubset += ",{'source':'anp'}"
	anp_flag= 'anp'
else:
	anp_flag=''


if form.getvalue('mostpop'):
	topwords = form.getvalue('mostpop')
else:
	topwords = "missing value for top words"

usersubset += ']}'
newssubset = ast.literal_eval(''.join(usersubset.split(',',1)))

#THE FOLLOWING IS STILL PROBLEMATIC. ONLY WORKS IF USER DIDN'T ENTER HIS OWN CUSTOMIZED ARGUMENT

if form.getlist('usersubset'):
	usersubset = ''.join(usersubset.split(',',1))
	usersubset = ''.join(usersubset.split(' ',1))


finalsubset = ast.literal_eval(usersubset)


if form.getvalue('year_start') and form.getvalue('month_start') and form.getvalue('day_start') and form.getvalue('year_end') and form.getvalue('month_end') and form.getvalue('day_end'):
	year_start = form.getvalue('year_start')
	month_start = form.getvalue('month_start')
	day_start = form.getvalue('day_start')
	year_end = form.getvalue('year_end')
	month_end = form.getvalue('month_end')
	day_end = form.getvalue('day_end')
	
	query_start = datetime.datetime(int(year_start),int(month_start),int(day_start))
	query_end = datetime.datetime(int(year_end),int(month_end),int(day_end))

	finalsubset['datum']={}
	finalsubset['datum']['$gte'] = query_start
	finalsubset['datum']['$lte'] = query_end

if form.getvalue('clean'):
	clean = True
else:
	clean = False

print('Content-Type: text/html')
print('''

<html>
<head>
<title>Wordcount analysis</title>
<link rel=StyleSheet href="../defaultstyle.css" type="text/css">
</head>
<body>
<h2>We are currently running an analysis on the top %s most common words from your selection of newspapers:</h2> </br>
<p>The subset you chose is: \t\t %s</p></br>
<pre><br><br>''' % (topwords,finalsubset))

c = frequenciesweb(int(topwords),clean,finalsubset)
mc = c.most_common(15)
wl = [w[0] for w in mc]

print('''<br><br>
<br>
</pre>
<h3> Download the list of words and their occurences</h3>
<p> The csv file can be downloaded by clicking <a href="http://infra.followthenews-uva.vm.surfsara.nl/tmp/wordcountoutput.csv">this link</a></p>
<br>
''')
basicfreq(wl,newssubset)
print('''
</body>
</html>
''')
