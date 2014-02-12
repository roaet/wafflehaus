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

import webob.dec
import webob.exc

from neutron import auth


class ContextFilter(object):
    """Attempts to create a context with the configured context class."""
    def __init__(self, app, conf):
        self.app = app
        self.conf = conf

    def _import_class(self, name):
        last_dot = name.rfind(".")
        kls = name[last_dot + 1: len(name)]
        module = __import__(name[0:last_dot], globals(), locals(), [kls])
        return getattr(module, kls)

    def _create_context(self, req):
        return self.app

    @webob.dec.wsgify
    def __call__(self, req):
        return self._create_context(req)


class TestContextFilter(ContextFilter):
    def _create_context(self, req):
        kls = self._import_class('tests.test_try_context.TestContextClass')
        context = kls()
        req.environ['test.context'] = context
        return self.app


class NeutronContextFilter(ContextFilter):
    def __init__(self, app, conf):
        super(NeutronContextFilter, self).__init__(app, conf)

    def _create_context(self, req):
        #NOTE(roaet): probably need to vet the req to this thing; headers?
        keystone_middleware = auth.NeutronKeystoneContext(self.app)
        return keystone_middleware(req)


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def try_context(app):
        strat = conf.get('context_strategy')
        if strat is None:
            msg = 'context_strategy is unset!'
            raise webob.exc.HTTPInternalServerError(msg)
        strat = strat.lower()
        if strat == 'none':
            return app
        if strat == 'test':
            return TestContextFilter(app, conf)
        if strat == 'neutron':
            return NeutronContextFilter(app, conf)
    return try_context
