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
from routes import Mapper

__all__ = ['matched_request', 'parse_resources']


def parse_resources(resources):
    result = {}
    if not resources:
        return
    work_list = [s.strip() for s in resources.split(',')]
    for res in work_list:
        res_split = res.split()
        methods = [m.upper() for m in res_split[:-1]]
        resource = res_split[-1]
        if resource not in result:
            result[resource] = []
        for m in methods:
            result[resource].append(m)
    return result


def matched_request(request, resource_list):
    if len(resource_list) == 0:
        return False
    map = Mapper()
    for resource, data in resource_list.iteritems():
        map.connect(None, resource, controller=','.join(data))
    res = map.routematch(request.path)
    if res is None:
        return False
    if request.method in res[0]['controller'].split(','):
        return True
    return False
