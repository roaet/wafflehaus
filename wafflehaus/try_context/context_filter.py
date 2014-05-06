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

import wafflehaus.base


class ContextFilter(wafflehaus.base.WafflehausBase):
    """Attempts to create a context with the configured context class."""
    def __init__(self, app, conf):
        super(ContextFilter, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log.info('Starting wafflehaus context middleware')
        self.context_key = conf.get('context_key')
        self.strat = conf.get('context_strategy')
        if self.strat is None:
            self.log.info('No context context is configured')

    def _import_class(self, name):
        last_dot = name.rfind(".")
        kls = name[last_dot + 1: len(name)]
        module = __import__(name[0:last_dot], globals(), locals(), [kls])
        return getattr(module, kls)

    def _create_context(self, req):
        if self.strat is None:
            return self.app
        try:
            kls = self._import_class(self.strat)
            if self.testing:
                self.log.info('Would be setting %s with %s' %
                              (self.context_key, self.strat))
        except ImportError:
            self.log.error("Could not find context strategy: %s" % self.strat)
            if not self.testing:
                return webob.exc.HTTPInternalServerError()
            else:
                self.log.error("Failed to find strategy: %s" % self.strat)
        if not self.testing:
            self.strat_instance = kls(self.context_key)
            self.strat_instance.load_context(req)
        return self.app

    @webob.dec.wsgify
    def __call__(self, req):
        if not self.enabled:
            return self.app

        return self._create_context(req)


class BaseContextStrategy(object):

    def __init__(self, key):
        self.key = key

    def load_context(self, req):
        pass


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def try_context(app):
        return ContextFilter(app, conf)
    return try_context
