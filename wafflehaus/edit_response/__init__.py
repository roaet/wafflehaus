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
from simplejson import JSONDecodeError

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

    def _replace_lookup(self, replace_str):
        if replace_str == '[]':
            return []
        if replace_str.lower() == 'null' or replace_str.lower() == 'none':
            return None
        if replace_str == '{}':
            return {}
        return replace_str

    def _foreach(self, conditional, data):
        if not isinstance(data, list):
            return data
        if not all(isinstance(item, dict) for item in data):
            return data
        new_data = []
        splits = conditional.split(":", 2)
        action = splits[1]
        conditionals = splits[2].split(',')
        for item in data:
            do_action = False
            for cond in conditionals:
                # TODO(jlh): Probably should support more than '='
                (target, value) = cond.split("=")
                if target not in item:
                    continue
                if item.get(target) == value:
                    do_action = True
            if do_action:
                if action == 'keep_if':
                    new_data.append(item)
            if not do_action:
                if action == 'drop_if':
                    new_data.append(item)
        self.log.debug('Replacing "{0}" with :"{1}"'.format(data, new_data))
        return new_data

    def _change_attribs(self, req, resp, resource):
        # Not sure recursion is the way here...
        def walk_keys(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == resource['key']:
                        val = resource.get('value', None)
                        if val is None:
                            del(data[key])
                            self.log.debug('Deleting "{0}":"{1}" from the '
                                           'response'.format(key, value))
                        elif val.startswith('foreach:'):
                            data[key] = self._foreach(val, data[key])
                        else:
                            replace = self._replace_lookup(resource['value'])
                            self.log.debug('Replacing "{0}":"{1}" with "{0}"'
                                           ':"{2}"'.format(key, value,
                                                           resource['value']))
                            data[key] = replace
                    else:
                        if isinstance(value, dict) or isinstance(value, list):
                            data[key] = walk_keys(value)
            elif isinstance(data, list):
                data = [walk_keys(part) for part in data]
            return data

        try:
            new_body = resp.json
            new_body = walk_keys(new_body)
            if 'http_status_code' in resource['key']:
                resource_val = resource['value']
                if resource_val.startswith('replace_if'):
                    (status_chk, status_repl) = resource_val.split(':')[1:3]
                    if str(resp.status_code) == status_chk:
                        self.log.debug('Replacing http status code "{0}" with '
                                       '"{1}"'.format(status_chk, status_repl))
                        resp.status_code = int(status_repl)
            resp.body = json.dumps(new_body)
        except JSONDecodeError:
            pass

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
