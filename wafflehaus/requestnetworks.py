# Copyright 2013 Openstack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging

import webob.dec
from webob import exc

from nova.api.openstack.compute import servers
from nova.api.openstack import wsgi
from nova.openstack.common import jsonutils
from nova import wsgi as base_wsgi


# NOTE(jkoelker) Make sure to log into the nova logger
log = logging.getLogger('nova.' + __name__)


class RequestNetworks(base_wsgi.Middleware):
    """RequestNetworks middleware checks for required networks from request
    """

    def __init__(self, application, **local_config):
        super(RequestNetworks, self).__init__(application)
        self.required_networks = local_config.get("required_nets", "")
        self.required_networks = [n.strip()
                                  for n in self.required_networks.split()]
        self.banned_networks = local_config.get("banned_nets", "")
        self.banned_networks = [n.strip()
                                for n in self.banned_networks.split()]
        self.xml_deserializer = servers.CreateDeserializer()

    @staticmethod
    def _get_networks(body):
        """extract networks from body
        """
        networks = body.get("networks")
        if not networks:
            return
        return [n["uuid"] for n in networks]

    def _get_servers_from_json(self, req):
        """extract body from json
        """
        body = jsonutils.loads(req.body)
        return self._get_networks(body["server"])

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
            log.info("No context found")
            return self.application

        projectid = context.project_id

        path = req.environ.get("PATH_INFO")
        if path is None:
            raise exc.HTTPUnprocessableEntity("Path is missing")

        pathparts = [part for part in path.split("/") if part]
        pathparts.insert(0, verb)
        pathparts = set(pathparts)
        bootcheck = set(["POST", projectid, "servers"])

        if (len(pathparts) == len(bootcheck) and
                len(pathparts.intersection(bootcheck)) == len(bootcheck)):
            if not req.body or len(req.body) == 0:
                raise exc.HTTPUnprocessableEntity("Body is missing")
            if req.content_type and "xml" in req.content_type:
                networks = self._get_servers_from_xml(req)
            else:
                networks = self._get_servers_from_json(req)
            # Required Networks
            msg = "Networks (%s) required but missing"
            if networks:
                network_list = ",".join(self.required_networks)
                for required_network in self.required_networks:
                    if required_network not in networks:
                        raise exc.HTTPForbidden(msg % network_list)
            # Banned (blacklist) Networks
            msg = "Networks (%s) banned and present"
            if networks:
                network_list = ",".join(self.banned_networks)
                for banned_network in self.banned_networks:
                    if banned_network in networks:
                        raise exc.HTTPForbidden(msg % network_list)

        return self.application
