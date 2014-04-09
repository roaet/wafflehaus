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
import webob.exc

try:
    from neutron import context
except ImportError:
    pass


class ContextFilter(object):
    """Attempts to create a context with the configured context class."""
    def __init__(self, app, conf):
        self.app = app
        self.conf = conf
        logname = __name__
        self.log = logging.getLogger(conf.get('log_name', logname))
        self.log.info('Starting wafflehaus context middleware')
        self.user_id = conf.get('user_id')
        self.testing = (conf.get('testing') in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))

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
        ctx = kls()
        req.environ['test.context'] = ctx
        return self.app


class NeutronContextFilter(ContextFilter):
    def __init__(self, app, conf):
        global context
        super(NeutronContextFilter, self).__init__(app, conf)
        self.neutron_ctx = None
        if context:
            self.neutron_ctx = context

    def _process_roles(self, roles):
        if not self.context.roles:
            self.context.roles = []
        if roles is None:
            return
        roles = [r.strip() for r in roles.split(',')]
        for role in roles:
            if role not in self.context.roles:
                self.context.roles.append(role)

    def _create_context(self, req):
        if self.neutron_ctx is None and not self.testing:
            ctx = self.neutron_ctx.get_admin_context()
            self.context = ctx
            self._process_roles(req.headers.get('X_ROLES', ''))
            req.environ['neutron.context'] = self.context
        return self.app


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
