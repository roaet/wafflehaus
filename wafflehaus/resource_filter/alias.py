# Copyright 2015 Rackspace Hosting
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
import wafflehaus.resource_filter as rf


class AliasResource(wafflehaus.base.WafflehausBase):

    def __init__(self, app, conf):
        super(AliasResource, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log.info('Starting wafflehaus resource alias middleware')
        self.resources = rf.parse_resources(conf.get('resource'))
        if 'addslash' in conf.get('action'):
            self.action = ['addslash', '']
        elif ':' not in conf.get('action', ''):
            self.action = ['400', "Bad Request"]
        else:
            self.action = conf.get('action').split(':', 1)[0]
        self.code = self.action[0]
        self.option = self.action[1]

    def _override(self, req):
        super(AliasResource, self)._override(req)
        new_resource = self._reconf(req, 'str', 'resource')
        if new_resource is not None:
            self.resources = rf.parse_resources(new_resource)

    def _perform_action(self, req):
        if self.code == 'subrequest':
            return
        if self.code == 'addslash':
            return webob.exc.HTTPMovedPermanently(add_slash=True)
        if self.code.isdigit():
            if int(self.code) < 400:
                return webob.exc.HTTPMovedPermanently(location=self.option)
            if int(self.code) < 500:
                return webob.exc.HTTPBadRequest(detail=self.option)

    @webob.dec.wsgify
    def __call__(self, req):
        super(AliasResource, self).__call__(req)
        if not self.enabled:
            return self.app

        if rf.matched_request(req, self.resources):
            self.log.info("Aliased " + str(req.path))
            return self._perform_action(req)
        return self.app


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def alias_resource(app):
        return AliasResource(app, conf)
    return alias_resource
