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
from tests import test_base

from wafflehaus.dns_filter import whitelist


class TestDNSFilter(test_base.TestBase):

    def test_create_dns_filter(self):
        result = whitelist.filter_factory({})
        self.assertIsNotNone(result)
