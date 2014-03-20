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

__all__ = ['set_default_payload', 'get_defaults']


def _walk_json_payload(payload, value, path, depth=0):
    key = path[depth]
    if len(path) - 1 == depth:
        if key not in payload:
            if value == 'null':
                value = None
            payload[key] = value
        return
    if key not in payload:
        return
    ptr = payload[key]
    if isinstance(ptr, list) and not isinstance(ptr, str):
        for child in ptr:
            _walk_json_payload(child, value, path, depth=depth + 1)
    else:
        _walk_json_payload(ptr, value, path, depth=depth + 1)


def json_set_unset_keys(payload, defaults):
    try:
        payload_json = json.loads(payload)
    except ValueError:
        return payload
    for default in defaults:
        _walk_json_payload(payload_json, default['value'], default['path'])
    return json.dumps(payload_json)


def get_defaults(defaults):
    result = []
    if not defaults:
        return result
    work_list = [s.strip() for s in defaults.split(',')]
    for working in work_list:
        parts = [s.strip() for s in working.split('=')]
        path = [s.strip() for s in parts[0].split(':')]
        value = parts[1]
        element = {}
        element['path'] = path
        element['value'] = value
        result.append(element)
    return result
