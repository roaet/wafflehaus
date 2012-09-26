"""
Created September 25, 2012

@author: Justin Hammond, Rackspace Hosting
"""

from webob import exc

from nova import wsgi


class RollRouter(wsgi.Middleware):

    def process_request(self, req, **local_config):
        pass
