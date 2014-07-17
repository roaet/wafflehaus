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

import json

from webob.dec import wsgify

from wafflehaus.base import WafflehausBase
import wafflehaus.resource_filter as rf


class EditResponse(WafflehausBase):

    def __init__(self, app, conf):
        super(EditResponse, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log.info('Starting wafflehaus edit attributes middleware')
        self.resources = {}
        resources = conf.get('resources')
        for resource in resources.split():
            self.resources[resource] = {
                'path': rf.parse_resources(conf.get('%s_path' % resource)),
                'key': conf.get('%s_key' % resource),
                'value': conf.get('%s_value' % resource)}
        return

    def _change_attribs(self, body_json, resource):
        body = json.loads(body_json)

        # This could be considerably better. Recursion, bleh.
        def walk_keys(data):
            for key, value in data.items():
                if key == resource['key']:
                    if resource['value'] is not None:
                        data[key] = resource['value']
                    else:
                        del(data[key])
                else:
                    if isinstance(value, dict):
                        data[key] = walk_keys(value)
            return data

        return json.dumps(walk_keys(body))

    @wsgify.middleware
    def __wrapped(self, app, req):
        for key, value in self.resources.items():
            if rf.matched_request(req, value['path']):
                resp = req.get_response(app)
                resp.body = self._change_attribs(resp.body, value)
        return self.app

    @wsgify
    def __call__(self, req):
        if not self.enabled:
            return self.app

        return self.__wrapped(self.app)


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def block_resource(app):
        return EditResponse(app, conf)

    return block_resource
