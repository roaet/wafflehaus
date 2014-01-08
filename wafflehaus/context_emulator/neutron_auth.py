# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright 2012 OpenStack Foundation
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

from oslo.config import cfg
import webob.dec
import webob.exc

from neutron import context
from neutron.openstack.common import log as logging
from neutron import wsgi

LOG = logging.getLogger(__name__)


class NeutronEmulatedKeystoneContext(wsgi.Middleware):


    @webob.dec.wsgify
    def __call__(self, req):
        LOG.debug("Waffling")
        LOG.debug(str(req.headers.items()))
        LOG.debug(str(req.body))
        return self.application
