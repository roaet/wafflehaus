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
import unittest2

#from neutron import context


class TestBase(unittest2.TestCase):
    '''Class to decide which unit test class to inherit from uniformly.'''

    def setUp(self):
        super(TestBase, self).setUp()
#        self.context = context.Context('fake', 'fake', is_admin=False)

#        class FakeContext(object):
#            def __new__(cls, *args, **kwargs):
#                return super(FakeContext, self).__new__(cls)
#
#            def __enter__(*args, **kwargs):
#                pass
#
#            def __exit__(*args, **kwargs):
#                pass
#
#        self.context.session.begin = FakeContext
