import datetime
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8180/")

_next = proxy.next()

# convert the ISO8601 string to a datetime object
print("Today: %s" % _next)

