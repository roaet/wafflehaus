"""
Created September 27, 2012

@author: Justin Hammond
"""
import logging

import webob.dec
from webob import exc

from nova.api.openstack import wsgi
from nova import wsgi as base_wsgi
from nova.api.openstack.compute import servers
from nova.openstack.common import jsonutils


class RequestNetworks(base_wsgi.Middleware):
    """RequestNetworks middleware checks for required networks from request
    """

    def __init__(self, application, **local_config):
        super(RequestNetworks, self).__init__(application)
        self.required_networks = local_config.get("required_nets", "")
        self.required_networks = [n.strip()
                                  for n in self.required_networks.split()]
        self.xml_deserializer = servers.CreateDeserializer()

    @staticmethod
    def _get_networks(body):
        """extract networks from body
        """
        networks = body["servers"].get("networks")
        if not networks:
            return
        return [n["uuid"] for n in networks]

    def _get_servers_from_json(self, req):
        """extract body from json
        """
        body = jsonutils.loads(req.body)
        return self._get_networks(body)

    def _get_servers_from_xml(self, req):
        """extract body from xml
        """
        body = self.xml_deserializer.default(req.body)
        return self._get_networks(body)

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
            if req.content_type and "xml" in req.content_type:
                networks = self._get_servers_from_xml(req)
            else:
                networks = self._get_servers_from_json(req)
            msg = "Network (%s) required but missing"
            for required_network in self.required_networks:
                if required_network not in networks:
                    raise exc.HTTPForbidden(msg % required_network)

        return self.application
