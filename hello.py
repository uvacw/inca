#!/usr/bin/env python3
import cgitb
import cgi
cgitb.enable()
print('Content-Type: text/html')
print()
print('''

<html>
<head>
<title>Hello World!</title>
</head>
<body>
<H1>Just trying VIM a bit</H1>
<p>
Alright we're just getting familiar with it
</p>
<ul>
<li> first element of list </li>
<li> second element of list </li>
<li> third element of list </li>
<li> Checking I'm still live updating with this fourth element </li>
Ik heet trouwens /usr/lib/cgi-bin/hello.py
<br>
Linkje voor Arno:<a href="http://www.tutorialspoint.com/python/python_cgi_programming.htm">cgi tutorial</a>
<form action="/cgi-bin/hello_get.py" method="post">
First Name: <input type="text" name="first_name"><br />
Last Name: <input type="text" name="last_name" />

<input type="submit" value="Submit" />
</form>
</body>
</html>
''')
