"""
Created September 20, 2012

@author: Justin Hammond, Rackspace Hosting
"""

from webob import exc

from nova import wsgi


DEFAULT_PUBLIC_NET = "00000000-0000-0000-0000-000000000000"
DEFAULT_SERVICE_NET = "11111111-1111-1111-1111-111111111111"


class RequestNetwork(wsgi.Middleware):

    def check_server_create(self, req, uuid_list, service_net):
        if req.method == "POST" and service_net not in uuid_list:
            return False
        return True

    def process_request(self, req, **local_config):
        return self.application
        service_net = local_config.get("service_net", DEFAULT_SERVICE_NET)
        # public_net = local_config.get("public_net", DEFAULT_PUBLIC_NET)
        if len(req.body) == 0:
            raise exc.HTTPUnprocessableEntity("Error: Zero length body")

        if not "server" in req.body:
            raise exc.HTTPUnprocessableEntity()

        server_dict = req.body["server"]
        requested_networks = server_dict.get("networks")

        uuid_list = []
        for network in requested_networks:
            uuid_list.append(network["uuid"])

        if not self.check_server_create(req, uuid_list, service_net):
            return None
        msg = ("Service net required in create for managed tenants ")
        raise exc.HTTPBadRequest(explanation=msg)
