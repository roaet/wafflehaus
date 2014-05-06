# Copyright 2013 Openstack Foundation # All Rights Reserved.
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
import webob
import webob.dec

import wafflehaus.base

log = logging.getLogger(__name__)


class RoleRouter(wafflehaus.base.WafflehausBase):
    """The purpose of this class is to route filters based on the role
    obtained from keystone.context.
    """

    def __init__(self, loader, conf):
        self.context_key = conf.get('context_key', 'nova.context')
        self.roles = {}
        self.routes = {}

        # This assumes roles are labeled role_<role> in conf
        routes = conf["routes"].split()
        for route in routes:
            key = "roles_%s" % route
            if key in conf:
                roles = conf[key].split()
                for role in roles:
                    self.roles[role] = route

        # This returns the particular route's app after applying the filters
        routes.append("default")
        for route in routes:
            key = "route_%s" % route
            if key in conf:
                pipeline = conf[key]
                pipeline = pipeline.split()
                filters = [loader.get_filter(f) for f in pipeline[:-1]]
                app = loader.get_app(pipeline[-1])
                filters.reverse()
                for f in filters:
                    app = f(app)
                self.routes[route] = app
                if key == 'default':
                    self.app = app
        super(RoleRouter, self).__init__(app, conf)

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        if not self.enabled:
            return self.app

        context = req.environ.get(self.context_key)

        if not context:
            log.info("No context found")
            return self.routes["default"]

        roles = context.roles
        for key in self.roles.keys():
            if key in roles:
                return self.routes[self.roles[key]]

        return self.routes["default"]


def rolerouter_factory(loader, global_conf, **local_conf):
    """Returns a WSGI composite app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    return RoleRouter(loader, conf)
