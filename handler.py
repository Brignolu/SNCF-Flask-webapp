from ladon.server.wsgi import LadonWSGIApplication
print('starting handler')
app = LadonWSGIApplication(['soapservice'],['soapservice.py'])
