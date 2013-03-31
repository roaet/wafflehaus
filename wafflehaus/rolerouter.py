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

from nova.api.openstack import wsgi


# NOTE(jkoelker) Make sure to log into the nova logger
log = logging.getLogger('nova.' + __name__)


def rolerouter_factory(loader, global_conf, **local_conf):
    return RoleRouter.factory(loader, global_conf, **local_conf)


class RoleRouter(object):
    """The purpose of this class is to route filters based on the role
    obtained from keystone.context
    """

    def __init__(self, routeinfo):
        self.routes = routeinfo["routes"]
        self.roles = routeinfo["roles"]

    @classmethod
    def factory(cls, loader, global_conf, **local_conf):
        routeinfo = {"roles": {}, "routes": {}}
        routes = local_conf["routes"]
        routes = routes.split()
        # get roles for routes
        for route in routes:
            key = "roles_%s" % route
            if key in local_conf:
                roles = local_conf[key]
                roles = roles.split()
                for role in roles:
                    routeinfo["roles"][role] = route

        # get pipeline for routes but add default route
        routes.append("default")
        for route in routes:
            key = "route_%s" % route
            if key in local_conf:
                pipeline = local_conf[key]
                pipeline = pipeline.split()
                filters = [loader.get_filter(n) for n in pipeline[:-1]]
                app = loader.get_app(pipeline[-1])
                filters.reverse()
                for filter in filters:
                    app = filter(app)
                routeinfo["routes"][route] = app
        return cls(routeinfo)

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        context = req.environ.get("nova.context")

        if not context:
            log.info("No context found")
            return self.routes["default"]

        roles = context.roles
        for key in self.roles.keys():
            if key in roles:
                return self.routes[self.roles[key]]
        return self.routes["default"]
