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
import dns.exception
import mock
import webob.exc

from wafflehaus.dns_filter import whitelist
from wafflehaus import tests


def do_lookup(address):
    if address == '192.168.1.1':
        return 'derp.widget.com'
    return 'something.bad.com'


def do_lookup_fail(address):
    if address == '192.168.1.1':
        return 'something.bad.com'
    return 'something.bad.com'


def do_lookup_unknown(address):
    raise dns.exception.DNSException


class FakeARecord(object):

    def __init__(self, good=True):
        if good:
            self.rrset = ['192.168.1.1']
        else:
            self.rrset = ['10.0.0.1']


class FakeResolver(object):

    def __init__(self, name=True):
        self.name = name

    def query(self, value, record_type):
        if record_type == 'PTR':
            return ['derp.widget.com'] if self.name else ['yo.bad.com']
        if record_type == 'A':
            if 'widget.com' in value:
                return FakeARecord()
            else:
                return FakeARecord(good=False)


class TestDNSFilter(tests.TestCase):

    def setUp(self):
        self.app = mock.Mock()
        self.conf_disabled = {'whitelist': 'widget.com'}
        self.conf = {'whitelist': 'widget.com', 'enabled': 'true'}
        self.testconf = {'whitelist': 'widget.com', 'testing': 'true',
                         'enabled': 'true'}
        self.mod_path = 'wafflehaus.dns_filter.whitelist.DNSWhitelist'
        self.addr_path = '%s.get_remote_addr' % self.mod_path
        self.resolver_path = '%s._create_resolver' % self.mod_path
        self.dns_reverse = 'dns.reversename.from_address'

        self.good_ip = '192.168.1.1'
        self.bad_ip = '10.0.0.1'

    def test_create_dns_filter(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        self.assertIsNotNone(result)

    def test_create_dns_filter_not_enabled_by_default(self):
        result = whitelist.filter_factory(self.conf_disabled)(self.app)
        self.assertIsNotNone(result)
        self.assertFalse(result.enabled)

    def test_match_ok(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

    def test_match_ok_with_forwarded_header(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.bad_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        ip_list = [self.good_ip, self.bad_ip]
        headers = {'X-Forwarded-For': ','.join(ip_list)}

        resp = result.__call__.request('/widget', method='POST',
                                       headers=headers)
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

# TESTING FUNCTIONS

    def test_no_fail_on_name_lookup_while_testing(self):
        result = whitelist.filter_factory(self.testconf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver(name=False)

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

    def test_no_fail_on_match_bad_address_while_testing(self):
        result = whitelist.filter_factory(self.testconf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.bad_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

    def test_no_fail_match_bad_name_while_testing(self):
        result = whitelist.filter_factory(self.testconf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['something.bad.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

    def test_no_fail_match_unknown_address_while_testing(self):
        result = whitelist.filter_factory(self.testconf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = [dns.exception.DNSException]

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

    def test_no_fail_no_dns_entries_while_testing(self):
        result = whitelist.filter_factory(self.testconf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertFalse(isinstance(resp, webob.exc.HTTPForbidden))

# END TESTING

    def test_fail_on_name_lookup(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver(name=False)

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertTrue(isinstance(resp, webob.exc.HTTPForbidden))

    def test_match_bad_address(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.bad_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertTrue(isinstance(resp, webob.exc.HTTPForbidden))

    def test_match_bad_name(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['something.bad.com']

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertTrue(isinstance(resp, webob.exc.HTTPForbidden))

    def test_match_unknown_address(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = [dns.exception.DNSException]

        resp = result.__call__.request('/widget', method='POST')
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertTrue(isinstance(resp, webob.exc.HTTPForbidden))

    def test_no_dns_entries(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(m_addr.called_once)
        self.assertTrue(isinstance(resp, webob.exc.HTTPForbidden))

    def test_no_whitelist_error(self):
        result = whitelist.filter_factory({'enabled': 'true'})(self.app)
        resp = result.__call__.request('/widget', method='POST')
        self.assertTrue(isinstance(resp, webob.exc.HTTPInternalServerError))

    def test_fail_with_empty_forwarded_header(self):
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.bad_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        headers = {'X-Forwarded-For': ''}

        resp = result.__call__.request('/widget', method='POST',
                                       headers=headers)
        self.assertEqual(1, m_addr.call_count)
        self.assertEqual(1, m_dns_rname.call_count)
        self.assertEqual(1, m_resolve.call_count)
        self.assertTrue(isinstance(resp, webob.exc.HTTPForbidden))

    def test_runtime_overrides(self):
        self.set_reconfigure()
        result = whitelist.filter_factory(self.conf)(self.app)
        m_addr = self.create_patch(self.addr_path)
        m_addr.return_value = self.good_ip

        m_resolve = self.create_patch(self.resolver_path)
        m_resolve.return_value = FakeResolver()

        m_dns_rname = self.create_patch(self.dns_reverse)
        m_dns_rname.side_effect = ['omg.widget.com']

        headers = {'X_WAFFLEHAUS_DNSWHITELIST_ENABLED': False}

        result.__call__.request('/widget', method='POST',
                                headers=headers)
        self.assertEqual(0, m_addr.call_count)
        self.assertEqual(0, m_dns_rname.call_count)
        self.assertEqual(0, m_resolve.call_count)
