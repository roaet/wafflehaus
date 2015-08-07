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

import mock
from mock import patch
from oslo_config import cfg
import unittest2


CONF = cfg.CONF


class TestCase(unittest2.TestCase):
    '''Class to decide which unit test class to inherit from uniformly.'''
    def setUp(self):
        super(TestCase, self).setUp()
        CONF.WAFFLEHAUS.runtime_reconfigurable = False
        self.app = mock.Mock()

    def set_reconfigure(self):
        CONF.WAFFLEHAUS.runtime_reconfigurable = True

    def create_patch(self, name, func=None):
        patcher = patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing
