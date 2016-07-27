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

from urlparse import urlparse
from urlparse import urlunparse

from webob.dec import wsgify

from wafflehaus.base import WafflehausBase


class Pagination(WafflehausBase):
    def __init__(self, app, conf):
        super(Pagination, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log.info('Starting wafflehaus pagination middleware')
        self.pagination_url = conf.get('pagination_url')
        # Disable if pagination_url is not found in api-paste.ini
        if not self.pagination_url:
            self.log.error(
                'wafflehaus pagination_url is missing in api-paste.ini')
            self.enabled = False

    @wsgify
    def __call__(self, req):
        """This returns an app if ignored or a response if processed."""
        super(Pagination, self).__call__(req)

        # The waffle must be enabled
        if not self.enabled:
            return self.app

        # If the app throws we log it and return
        try:
            resp = req.get_response(self.app)
        except Exception as e:
            self.log.debug(('pagination wafflehaus error in get_response:'
                           '{}'.format(e)))
            return self.app

        if not resp:
            return self.app

        if resp.status_code != 200:
            return self.app

        # Build a list of possible pagination keywords.
        # This will look for things such as:
        #   - networks_links;
        #   - subnets_links;
        #   - security_groups_links;
        #   - ports_links;
        #   - subnetpools_links.
        try:
            link_type_list = filter(lambda kw: '_links' in kw, resp.json)
        except ValueError:
            self.log.debug('pagination wafflehaus: JSON decoding failed')
            return self.app

        # If the list is empty, we have nothing to process.
        if len(link_type_list) == 0:
            return self.app

        # List is not empty, take the first element.
        link_type = link_type_list[0]

        # init the json that we will return from the passed response
        pagination_json = resp.json
        pagination_json[link_type] = []

        # Replace all href url occurrences with the ones from the config file.
        for link in resp.json[link_type]:
            passed_url = urlparse(link['href'])
            new_url = urlparse(self.pagination_url)
            url = passed_url._replace(netloc=new_url.netloc,
                                      scheme=new_url.scheme)
            link['href'] = urlunparse(url)
            pagination_json[link_type].append(link)

        # Replace the json with the new containing fixed links
        resp.json = pagination_json

        return resp


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def wrapper(app):
        return Pagination(app, conf)

    return wrapper
