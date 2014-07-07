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

from oslo.config import cfg
import webob.request

GLOBAL_CONF = cfg.CONF

wafflehaus_global_opts = [
    cfg.BoolOpt('runtime_reconfigurable', default=False,
                help='Will enable header reconfiguration'),
]

GLOBAL_CONF.register_opts(wafflehaus_global_opts, 'WAFFLEHAUS')


class WafflehausBase(object):

    def __init__(self, app, conf):
        self.conf = conf
        self.app = app
        self.header_prefix = 'X_WAFFLEHAUS'
        self.truths = (True, 'True', 'true', 't', '1', 'on', 'yes', 'y')
        logname = __name__
        self.log = logging.getLogger(conf.get('log_name', logname))
        self.testing = (conf.get('testing') in self.truths)
        self.enabled = (conf.get('enabled', False) in self.truths)
        self.reconfigure = GLOBAL_CONF.WAFFLEHAUS.runtime_reconfigurable

    def _override(self, req):
        if not isinstance(req, webob.request.BaseRequest):
            """Ensure that the request is not a mock"""
            return
        name = self.__class__.__name__

        header_enabled = "%s_%s_ENABLED" % (self.header_prefix, name.upper())
        if header_enabled in req.headers:
            val = req.headers[header_enabled]
            self.enabled = val in self.truths

        header_testing = "%s_%s_TESTING" % (self.header_prefix, name.upper())
        if header_testing in req.headers:
            val = req.headers[header_testing]
            self.testing = val in self.truths

    def _override_caller(self, req):
        if not self.reconfigure:
            return
        self._override(req)

    def __call__(self, req):
        self._override_caller(req)
