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
from nova import compute
from nova.compute import utils as compute_utils
from nova.openstack.common import uuidutils
from nova import wsgi as base_wsgi


log = logging.getLogger('nova.' + __name__)


def _translate_vif_summary_view(_context, vif):
    """Maps keys for VIF summary view."""
    d = {}
    d['id'] = vif['id']
    d['mac_address'] = vif['address']
    d['ip_addresses'] = vif['ip_addresses']
    return d


class DetachNetworkCheck(base_wsgi.Middleware):
    """DetachNetworkCheck middleware ensures certain networks are not
    detached
    """

    def __init__(self, application, **local_config):
        super(DetachNetworkCheck, self).__init__(application)
        self.compute_api = compute.API()
        self.required_networks = local_config.get("required_nets", "")
        self.required_networks = [n.strip()
                                  for n in self.required_networks.split()]
        self.xml_deserializer = servers.CreateDeserializer()

    def _get_network_info(self, req, server_id, entity_maker):
        """Returns a list of VIFs, transformed through entity_maker"""
        context = req.environ['nova.context']

        instance = self.compute_api.get(context, server_id)
        nw_info = compute_utils.get_nw_info_for_instance(instance)
        vifs = []
        for vif in nw_info:
            addr = [dict(network_id=vif["network"]["id"],
                         network_label=vif["network"]["label"],
                         address=ip["address"]) for ip in vif.fixed_ips()]
            v = dict(address=vif["address"],
                     id=vif["id"],
                     ip_addresses=addr)
            vifs.append(entity_maker(context, v))

        return {'virtual_interfaces': vifs}

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req, **local_config):
        verb = req.method
        if verb != "DELETE":
            return self.application

        context = req.environ.get("nova.context")
        if not context:
            log.info("No context found")
            return self.application

        projectid = context.project_id
        path = req.environ.get("PATH_INFO")
        if path is None:
            raise exc.HTTPUnprocessableEntity("Path is missing")

        pathparts = [part for part in path.split("/") if part]
        if len(pathparts) != 5:
            return self.application
        if (pathparts[0] != projectid or
                pathparts[1] != "servers" or
                pathparts[3] != "os-virtual-interfacesv2"):
            return self.application

        server_uuid = pathparts[2]
        vif_uuid = pathparts[4]
        if (not uuidutils.is_uuid_like(server_uuid) or
                not uuidutils.is_uuid_like(vif_uuid)):
            return self.application

        #at this point we know it is the correct call
        ent_maker = _translate_vif_summary_view
        network_info = self._get_network_info(req, server_uuid,
                                              entity_maker=ent_maker)

        msg = "Network (%s) cannot be detached"
        network_list = ",".join(self.required_networks)
        for vif in network_info["virtual_interfaces"]:
            if vif['id'] == vif_uuid:
                ip_info = vif['ip_addresses']
                network_id = ip_info[0]['network_id']
                if network_id in self.required_networks:
                    log.info("waffle - attempt to detach required network")
                    raise exc.HTTPForbidden(msg % network_list)

        return self.application
