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
from routes import Mapper

import webob.dec
import webob.exc


class BlockResource(object):

    def _parse_resources(self, resources):
        self.resources = {}
        if not resources:
            return
        work_list = [s.strip() for s in resources.split(',')]
        for res in work_list:
            res_split = res.split()
            methods = [m.upper() for m in res_split[:-1]]
            resource = res_split[-1]
            if resource not in self.resources:
                self.resources[resource] = []
            for m in methods:
                self.resources[resource].append(m)

    def __init__(self, app, conf):
        self.app = app
        self.conf = conf
        logname = __name__
        self.log = logging.getLogger(conf.get('log_name', logname))
        self.log.info('Starting wafflehaus resource blocker middleware')
        self.user_id = conf.get('user_id')
        self.testing = (conf.get('testing') in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))

        self._parse_resources(conf.get('resource'))

    def _check_resource(self, req):
        if len(self.resources) == 0:
            return self.app
        map = Mapper()
        for resource, data in self.resources.iteritems():
            map.connect(None, resource, controller=','.join(data))
        res = map.routematch(req.path)
        if res is None:
            return self.app
        if req.method in res[0]['controller'].split(','):
            return webob.exc.HTTPForbidden()
        return self.app

    @webob.dec.wsgify
    def __call__(self, req):
        return self._check_resource(req)


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def block_resource(app):
        return BlockResource(app, conf)
    return block_resource
