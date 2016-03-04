#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable()
form = cgi.FieldStorage()
first_name = form.getvalue('first_name')
last_name = form.getvalue('last_name')

print('Content-Type: text/html')
print('''

<html>
<head>
<title>This is the demo newspaper choice Program</title>
</head>
<body>
<h2>We are currently running an analysis on: %s, %s</h2>''' % (first_name,last_name))
print(''' 
</body>
</html>
''')
