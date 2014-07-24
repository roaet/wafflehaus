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
        self.log.info('Starting wafflehaus edit_response middleware')
        self.resources = {}
        filters = conf.get('filters')
        if filters is None:
            self.log.warning("EditResponse waffle could not find any filters"
                             " in its configuration")
            return
        for resource_filter in filters.split():
            if resource_filter in self.resources.keys():
                self.log.warning("EditResponse waffle found two filter names "
                                 "with the same name (first now overridden")
            self.resources[resource_filter] = {
                "resource": rf.parse_resources(
                    conf.get("%s_resource" % resource_filter)),
                "key": conf.get("%s_key" % resource_filter),
                "value": conf.get("%s_value" % resource_filter)}
        return

    def _change_attribs(self, req, resp, resource):
        # Not sure recursion is the way here...
        def walk_keys(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == resource['key']:
                        if resource['value'] is not None:
                            self.log.debug('Replacing "{0}":"{1}" with "{0}"'
                                           ':"{2}"'.format(key, value,
                                                           resource['value']))
                            data[key] = resource['value']
                        else:
                            del(data[key])
                            self.log.debug('Deleting "{0}":"{1}" from the '
                                           'response'.format(key, value))
                    else:
                        if isinstance(value, dict) or isinstance(value, list):
                            data[key] = walk_keys(value)
            elif isinstance(data, list):
                    data = [walk_keys(part) for part in data]
            return data

        new_body = resp.json
        new_body = walk_keys(new_body)
        resp.body = json.dumps(new_body)
        return resp

    @wsgify
    def __call__(self, req):
        """Returns a response if processed or an app if skipped."""
        super(EditResponse, self).__call__(req)
        resp = None

        if not self.enabled:
            return self.app
        if hasattr(self, "resources"):
            for resource_filter in self.resources.keys():
                if rf.matched_request(
                        req, self.resources[resource_filter]["resource"]):
                    if resp is None:
                        resp = req.get_response(self.app)
                    resp = self._change_attribs(
                        req, resp, self.resources[resource_filter])
        if resp is None:
            return self.app
        else:
            return resp


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def wrapper(app):
        return EditResponse(app, conf)

    return wrapper
