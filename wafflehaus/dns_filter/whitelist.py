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
"""This middleware is intended to be used with paste.deploy."""
import webob.dec
import webob.exc

import dns.exception
import dns.resolver
import dns.reversename

import wafflehaus.base


# pylint: disable=R0903
class DNSWhitelist(wafflehaus.base.WafflehausBase):
    """DNSWhitelist middleware will DNS lookup REMOTE_ADDR and attempt to
    match result to a whitelist. A failed match will 403.
    """

    def __init__(self, app, conf):
        super(DNSWhitelist, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log.info('Starting wafflehaus dns whitelist middleware')
        self.ignore_forwarded = (conf.get('ignore_forwarded') in
                                 (True, 'true', 't', '1', 'on', 'yes', 'y'))
        self.whitelist = self._create_whitelist(conf.get('whitelist'))

    def _create_resolver(self):
        """Creates the DNS resolver."""
        nameserver = str(dns.resolver.Resolver().nameservers[0])
        nameserver = self.conf.get('nameserver', nameserver)
        res = dns.resolver.Resolver(configure=False)
        res.nameservers = [nameserver]
        return res

    def _create_whitelist(self, whitelist):
        """Creates the whitelist from configuration or testing whitelists."""
        result = None
        if self.testing:
            test_list = ['rackspace.com']
            result = test_list
        if whitelist is not None:
            result = whitelist.split(" ")
        return result

    def check_reverse_dns(self, ip_address, a_record_rrset):
        """Checks to ensure IP is within a set of IPs from an A query set."""
        match = any(ip_address == str(val) for val in a_record_rrset)
        return match

    def check_domain_to_whitelist(self, domain):
        """Checks to ensure a domain ends with at least one of a whitelisted
        domain-ending string.
        """
        self.log.info("Checking " + str(domain))
        if domain.endswith('.'):
            domain = domain[:-1]
        for ok_host in self.whitelist:
            if domain.endswith(ok_host):
                return True
        return False

    def get_remote_addr(self, request):
        return request.remote_addr

    def parse_x_forwarded_for(self, xforward):
        """It is a CSV list of IPs."""
        self.log.info("Forwarded is : " + str(xforward))
        ip_list = xforward.split(',')
        if len(ip_list):
            return ip_list[0]
        return None

    @webob.dec.wsgify
    def __call__(self, req):
        """Performs white listing of REMOTE_ADDR and will fail if:
            - PTR query of REMOTE_ADDR does not end with a whitelisted domain
            - A query of PTR query fails to match REMOTE_ADDR
        """
        if not self.enabled:
            return self.app

        if not self.whitelist:
            self.log.error("Whitelist not set")
            return webob.exc.HTTPInternalServerError()

        remote_addr = self.get_remote_addr(req)

        if 'X-Forwarded-For' in req.headers and not self.ignore_forwarded:
            remote_addr = self.parse_x_forwarded_for(
                req.headers['X-Forwarded-For'])
            if remote_addr is None:
                return webob.exc.HTTPForbidden()

        if self.testing:
            remote_addr = self.conf.get('testing_remote_addr', remote_addr)

        self.log.debug("DNS check of %s against %s" % (remote_addr,
                                                       str(self.whitelist)))

        res = self._create_resolver()

        try:
            name = dns.reversename.from_address(remote_addr)
            self.log.info("name is : " + str(name))
            ptr = res.query(name, "PTR")[0]
            self.log.info('ptr is ' + str(ptr))

            if not self.check_domain_to_whitelist(str(name)):
                self.log.warning("DNS whitelist matching failure")
                if not self.testing:
                    return webob.exc.HTTPForbidden()
                else:
                    return self.app

            a_record = res.query(str(ptr), "A")
            self.log.info('a record is : ' + str(a_record))
        except dns.exception.DNSException:
            msg = "Missing DNS entries?"
            self.log.error("DNS Error during query: " + msg)
            if not self.testing:
                return webob.exc.HTTPForbidden()
            else:
                return self.app

        if not self.check_reverse_dns(remote_addr, a_record.rrset):
            if self.testing:
                self.log.warning("Reverse DNS check failed")
            else:
                self.log.warning("Reverse DNS check failed")
                return webob.exc.HTTPForbidden()
        return self.app


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def auth_bypass(app):
        """Returns the app for paste.deploy."""
        return DNSWhitelist(app, conf)
    return auth_bypass
