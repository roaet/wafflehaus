"""
Created September 27, 2012

@author: Justin Hammond
"""
import logging

import webob.dec
from webob import exc

from nova.api.openstack import wsgi
from nova import wsgi as base_wsgi
from nova.openstack.common import jsonutils


logging.basicConfig()

DEFAULT_PUBLIC_NET = "00000000-0000-0000-0000-000000000000"
DEFAULT_SERVICE_NET = "11111111-1111-1111-1111-111111111111"


class RequestNetworks(base_wsgi.Middleware):

    def __init__(self, application, **local_config):
        super(RequestNetworks, self).__init__(application)
        self.public_net = local_config.get("public_net", DEFAULT_PUBLIC_NET)
        self.service_net = local_config.get("service_net", DEFAULT_SERVICE_NET)

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req, **local_config):
        verb = req.method
        context = req.environ.get("nova.context")

        if not context:
            logging.info("No context found")
            return self.application

        projectid = context.project_id

        path = req.environ.get("PATH_INFO")
        if path is None:
            raise exc.HTTPUnprocessableEntity("Path is missing")

        pathparts = path.split("/")
        pathparts.insert(0, verb)
        pathparts = set(pathparts)
        bootcheck = set(["POST", projectid, "servers"]) 

        if len(pathparts.intersection(bootcheck)) == len(bootcheck):
            if not req.body or len(req.body) == 0:
                raise exc.HTTPUnprocessableEntity("Body is missing")
            body = jsonutils.loads(req.body)
            networks = body["server"]["networks"]
            has_service = False
            has_public = False
            for net in networks:
                if net["uuid"] == self.service_net:
                    has_service = True
                elif net["uuid"] == self.public_net:
                    has_public = True
            msg = "Service net required but missing"
            if not has_service:
                raise exc.HTTPUnprocessableEntity(msg)

        return self.application
