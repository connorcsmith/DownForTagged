#!/usr/bin/python

# Take in a domain or url from a form, determine which it is, then check to see if it's up.
# Calls DownOrNot.py for most of its functions.  Also uses the cgi and cgitb.

import cgi
import cgitb

cgitb.enable()

# Boilerplate HTML headers
print 'Content-type: text/html\n'
print '<html>'
print '<h1>Please enter a domain, URL, or IP address. </h1>'
print '<form action="downOrNot.cgi" method="get">'
print 'Keyword: <input type="text" name="address">  <br />'
print '<input type="submit" value="Submit" />'
print '</form>'
print '</html>'
