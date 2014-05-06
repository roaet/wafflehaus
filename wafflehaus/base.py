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


class WafflehausBase(object):

    def __init__(self, app, conf):
        self.conf = conf
        self.app = app
        logname = __name__
        self.log = logging.getLogger(conf.get('log_name', logname))
        self.testing = (conf.get('testing') in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))
        self.enabled = (conf.get('enabled', False) in
                        (True, 'true', 't', '1', 'on', 'yes', 'y'))
