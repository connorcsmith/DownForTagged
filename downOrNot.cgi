#!/usr/bin/python
#
# This file determines whether a URL, Domain, or IP is currently up or down.  
#
# In the case of 

import urllib2
import urlparse
import socket
import os 

# Basic cgi headers
import cgi
import cgitb

cgitb.enable()


# Flag this to set whether to be verbose about the error codes we're getting

debug = False


# Method to split a cname into a subdomain, domain, and tld from a URL
def domainRetrieveFromURL(url):
    try:
        testUrl = urlparse.urlparse(url)
        tld =  testUrl.hostname.split('.')[-2] + '.' + testUrl.hostname.split('.')[-1]
        domain = testUrl.hostname.split('.')[-1]
        fullDomain = testUrl
        return (tld, domain, fullDomain)
    except:
        print "I couldn't make sense of the URL!"
        
# Method to split a cname into a subdomain, domain, and tld from a FQDN
def domainRetrieveFromFQDN(fqdn):
    try:
        tld = fqdn.hostname.split('.')[-1]
        domain = fqdn.hostname.split('.')[-2] + '.' + fqdn.hostname.split('.')[-1]
        fullDomain = fqdn
        return (tld, domain, fullDomain)
    except:
        print "I couldn't make sense of the FQDN!"


# Method to try a fully qualified HTTP domain
def urlRetrieve(url):
    try:
        urllib2.urlopen(url, timeout=1)
        return True
    except urllib2.URLError as badURL:
        if debug: print badURL.reason
        pass
    except urllib2.URLError as badHTTPResponse:
        if debug: print badHTTPResponse.code
        pass
    return False


# Method to see if this is an IP address
def isIP(testValue):
    # Use the socket library to avoid writing a horrifyingly ugly regex; i.e. you're not
    # just looking for "not numbers," you're also trying to avoid having things like 
    # 256.256.256.0 running around unchecked.
    
    # Technically, this function is really designed to pack an IP address from canonical
    # xxx.xxx.xxx.xxx into 4 8-bit octets.  We're hijacking it to check if this is an IP
    # or not.
    #
    # A good response here means the thing is a valid IP
    try:
        socket.inet_aton(testValue)
        return True
    
    # Any error here means it isn't
    except:
        return False
    
# Method to see if this is an internet domain with a valid aname record
#
# CAUTION: THIS CODE USES THE OS MODULE TO ALLOW AN NSLOOKUP TO OCCUR.
# THIS IS AN ENORMOUS SECURITY HOLE.
# IF YOU HAVE ANY CONCERNS ABOUT USING THIS CODE, IT SHOULD NOT BE EXPOSED TO THE OUTSIDE
# WORLD.
# 
# Take in a string, put out a bool with the validity of the hostname
def isResolvableDomain(testValue):
    # Perform os-level nslookup of hostname
    #
    # A good response means it's a valid domain
    try:
        os.system("nslookup " + testValue)
        return True
    
    #Any error here means it isn't.
    except:
        return False
        
# Method to use the socket library's getaddrinfo to return information on valid hosts
# If the user doesn't put in a port here, assume 80
#
# The only reason to use the unsafe function is to deal with a domain that is, indeed down.
# The question is whether or not you really want to deal with the risk of a potential buffer
# overflow or other attack.
def saferIsValidDomain(testValue, testPort=80):
    # Perform sockets-library nslookup of hostname
    #
    # A good response means it's a valid domain, and the port we've given is open
    try:
        socket.getaddrinfo(testValue, testPort)
        return True
    
    #Any error here means one of the above isn't true.
    except:
        return False


# Method to check if this is a valid URL.
def isURL(testValue):
    # Perform urllib2-library connection for hostname
    #
    # A good response means it's a valid URL, and it's open
    try:
        urllib2.urlopen(testValue)
        return True
    # A URLError means it was a valid URL, for a known protocol, but didn't work.
    # That's OK, we can still work with that, but need to figure out if it's up.
    except urllib2.URLError:
        return True
    # Anything else here, means it wasn't a valid URL, and is never going to be.
    except:
        return False
        
# This method wraps all the isXXX methods.  This returns two values, one
# listing if it's a URL, domain, IP address, or rubbish
def whatKindOfResourceIsThis(questionableAddress):

    try:
        # Easiest to tell is if it's an IP
        if isIP(questionableAddress):
            return "IP"
        # Then domain
        elif saferIsValidDomain(questionableAddress):
            return "Domain"
        # Then URL (this actually attempts to connect to something, so it shouldn't be
        # run unless we absolutely have to.
        elif isURL(questionableAddress):
            return "URL" 
        # Otherwise, it's either garbage or unresolvable
        else:
            return "Unresolvable"
    except: 
        print "Something very bad happened here.  All of the checks here should've had handled"
        print "exceptions therein without having any issues whatsoever.  IF you're seeing this,"
        print "something broke."
        
# This method attempts to take a connection address, and type and attempt to create a socket 
# to it.  It returns True/False, based on the results
# Valid types are "Domain", "URL", "IP", and "Unresolvable."
def upOrDown(address, addressType): 
    # For the record, I dislike there isn't a switch block in Python
    # Add on an http for Domains and IPs
    if (addressType=="Domain") or (addressType=="IP"):
        try:
            urllib2.urlopen("http://" + address)
            return True
        except:
            return False
    #if it's a URL, I'll let them specify the protocol
    elif addressType=="URL":
        try:
            urllib2.urlopen(address)
            return True
        except:
            return False
    #If it's anything else, why even bother?
    else:
            return False     

# Boilerplate HTML headers
print 'Content-type: text/html\n'
print '<html>'

# get entered form data out of the previous page
form = cgi.FieldStorage()

if "address" not in form :
    print "<H1>Error</H1>"
    print "Please fill in the address field.  Hit the back button to continue."
else:
    address = form.getvalue('address')
    if type(address) is not str:
            print "<H1>Error</H1>"
            print address
            print "Please put only one address in the address field.  Hit the back button to continue."
    else:
        addressType = whatKindOfResourceIsThis(address)
        print "<H1>Test Complete:<H1>"
        print "Address \"" + address + "\" is currently reporting status: ",
        if upOrDown(address, addressType):
            print " up!"
        else:
            print " *NOT* up!"

print '</html>'
