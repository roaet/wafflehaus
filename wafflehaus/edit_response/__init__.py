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
        resources = rf.parse_resources(conf.get('resources'))
        return

    def _change_attribs(self, req, resp):
        resp_body = resp.json

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

    @wsgify
    def __call__(self, req):
        if not self.enabled:
            return self.app
        if rf.matched_request(req, self.resources):
            resp = req.get_response(app)
            resp = self._change_attribs(req, resp)
        return resp


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def block_resource(app):
        return EditResponse(app, conf)

    return block_resource
