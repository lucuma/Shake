# -*- coding: utf-8 -*-
"""
    manage.py
    ----------------------------------------------
        
    Admin functions

"""
from shake import manager

from web.app import app


@manager.command
def run(host=None, port=None, **kwargs):
    """[-host HOST] [-port PORT]
    Runs the application on the local development server.
    """
    app.run(host, port, **kwargs)


@manager.command
def run_wsgi():
    """
    Run the application using the WSGI protocol."""
    application = app


@manager.command
def run_fastcgi(protocol='fcgi', host='localhost', port=8080, socket=''
    , method='prefork', pidfile='', maxspare=5, minspare=2
    , maxchildren=50, maxrequests=0):
    """[-protocol (fcgi|scgi)] ([-host HOST] [-port PORT]|-socket SOCKET) \
    [-method (prefork|threaded)] [-pidfile PIDFILE] [-maxspare MAXSPARE] \
    [-minspare INT] [-maxchildren MAXCHILDREN] [-maxrequests MAXREQUESTS]
    Run the application using the FastCGI protocol.
    
    Requieres the flup python package: http://www.saddi.com/software/flup/
    
    protocol:
        Either 'fcgi' or 'scgi'. Default 'fcgi'.
    
    host:
        Host to listen on. Default 'localhost'.
    
    port:
        Port to listen on. Default `8080`. 
    
    socket:
        UNIX socket to listen on.
        
    method:
        Either 'prefork' or 'threaded'. Default 'prefork'.
        
    maxrequests:
        Number of requests a child handles before it is killed and a new child 
        is forked (0 = no limit). Default `0`.
        
    maxspare:
        Max number of spare processes / threads. Default `5`.
        
    minspare:
        Min number of spare processes / threads. Default `2`.
        
    maxchildren:
        Hard limit number of processes / threads. Default `50`.
    
    maxrequests:
        Hard limit number of accepted requests (0 = no limit). Default `0`.
        
    pidfile:
        Write the spawned process-id to this file.
    
    """
    try:
        import flup
    except ImportError:
        raise ImportError('Unable to load the flup package. \n'
            ' In order to run the application as FastCGI, you will'
            ' need to get flup from http://www.saddi.com/software/flup/'
            '  If you\'ve already installed flup, then make sure you have '
            ' it in your PYTHONPATH.')
    import os
    from werkzeug.utils import import_string
    
    flup_module = 'flup.server.' + protocol
    
    assert method in ('prefork', 'threaded'), ('Implementation must be'
        ' one of prefork or threaded.')
    
    if method == 'prefork':
        wsgi_opts = {
            'maxSpare': int(maxspare),
            'minSpare': int(minspare),
            'maxChildren': int(maxchildren),
            'maxRequests': int(maxrequests),
            }
        flup_module += '_fork'
    elif method == 'threaded':
        wsgi_opts = {
            'maxSpare': int(maxspare),
            'minSpare': int(minspare),
            'maxThreads': int(maxchildren),
            }
    
    wsgi_opts['debug'] = bool(app.settings.DEBUG)
    
    try:
        WSGIServer = import_string('%s.WSGIServer' % flup_module)
    except ImportError:
        raise ImportError('Unable to import the WSGIServer from the'
            ' flup package')
    
    wsgi_opts['bindAddress'] = socket
    if not socket:
        wsgi_opts['bindAddress'] = (host, int(port))
    
    if pidfile:
        filep = open(pidfile, "w")
        filep.write("%d\n" % os.getpid())
        filep.close()
    
    WSGIServer(app, **wsgi_opts).run()



if __name__ == "__main__":
	manager.run()

