#!/usr/bin/python

# Ordinarily, you shouldn't pull in the entire module for these, especially for cgi - tends to junk 
# up your namespace

import urllib2
import cgi
import urlparse
import socket
import os 

# Flag this to set whether to be verbose about the error codes we're getting

debug = True

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
def isValidDomain(testValue):
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
# The question is whether or not you really want to deal with the risk of a potential buffer overflow or 
# other attack.
#
# Better safe than sorry.
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
    

def attemptDomainConnect(url):
    
    # Attempt to connect to the desired URL.  If it works, that means the site can talk to the remote
    # host.  Assuming it doesn't, it attempts to do the following:
    #    1) Attempts to connect to the subdomain in the URL
    #    2) Attempts to connect to the domain in the URL
    #    TO DO:  3) Attempts ICMP to the subdomain in the URL
    #    TO DO:  4) Attempts ICMP to the domain in the URL
    #
    #    
    
    try:
        
        # Get the domain, TLD, and subdomain info
        testTLD, testDomain, testFullDomain = domainRetrieve(url)
        
        # Attempt to pull the URL with no further cleanup on it
        if urlRetrieve(url):
            
            # We found it, so notify the user, and stop trying.
            print "Unfortunately the URL \" " + url + "\" seems to be up."
            
        else:
                
            # We didn't get the full URL, so try the subdomain, and see if the user
            # fat-fingered the target page
            
            if (urlRetrieve(testFullDomain) == True):
                
                # We found the subdomain, just not the URL the user was looking for
                # so notify them and stop trying.
                print "The URL \" " + url + "\" seems not to be responding."
                print "It's parent domain, \"" + testFullDomain + "\"however, is."
                print "Have you checked the page you're looking for is available?"
                
            elif testDomain != testFullDomain: 
                
                # We didn't find the subdomain, and the full domain are different, so let's 
                # try the full domain
                
                if (urlRetrieve(testDomain) == True):
                
                    print "The URL \" " + url + "\" seems not to be responding."
                    print "It's base domain, \"" + testDomain + "\"isn't either."
                
            else: 
                #code for ICMP for the subdomain goes here.
                pass
                
                if testDomain != testFullDomain: 
                    pass
                    #code for the ICMP test for the domain goes here.
                    
    except:
        print "Something awful and unexpected happened here."

google="http://www.google.com"
attemptDomainConnect(google)
