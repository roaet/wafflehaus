"""
Created September 27, 2012

The purpose of this class is to test injection of a middleware into devstack.

@author: Justin Hammond
"""
import logging

from nova import wsgi as base_wsgi


logging.basicConfig()


class TestMiddleware(base_wsgi.Middleware):
    """The purpose of this class is to test injection of a middleware into
    devstack.
    """

    def __call__(self, req):
        context = req.environ.get("nova.context")
        logging.info(context)
        return self.application
