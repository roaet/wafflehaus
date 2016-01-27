# Copyright 2016 Justin Hammond
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
import time

import webob.dec
import webob.exc

import wafflehaus.base


FAKE_REQ_ID = 'req-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
FAKE_TENANT_ID = '-'


class RequestResponseLogger(wafflehaus.base.WafflehausBase):

    def __init__(self, app, conf):
        super(RequestResponseLogger, self).__init__(app, conf)
        self.log.name = conf.get('log_name', __name__)
        self.log_file = conf.get('log_file')
        self.context_key = conf.get('context_key')
        self.separator = conf.get('separator', ' ')
        default_format = '%(message)s' + self.separator + '%(asctime)s'
        self.log_format = conf.get('logformat', default_format)
        if self.log_file is not None:
            formatter = logging.Formatter(self.log_format)
            self.log = logging.getLogger(self.log.name)
            self.log.handlers = []
            fileHandler = logging.FileHandler(self.log_file)
            fileHandler.setFormatter(formatter)
            self.log.addHandler(fileHandler)
            self.log.propagate = False
            self.log.info('Starting wafflehaus request/response logger')
        else:
            self.enabled = False

    @webob.dec.wsgify
    def __call__(self, req):
        super(RequestResponseLogger, self).__call__(req)
        if not self.enabled:
            return self.app

        start = time.time()
        resp = req.get_response(self.app)
        end = time.time()
        difference = (end - start)

        request_id = FAKE_REQ_ID
        tenant_id = 'admin'
        contents = []
        ctx = req.environ.get(self.context_key)
        if ctx is not None:
            request_id = ctx.request_id
            if ctx.tenant_id is not None:
                tenant_id = ctx.tenant_id
        contents.append("%dms" % difference)
        contents.append("%d" % resp.status_int)
        contents.append('<--')
        contents.append(request_id)
        contents.append(tenant_id)
        contents.append(req.method)
        contents.append(req.path)
        contents.append("(%s)" % req.query_string)

        log_str = self.separator.join(contents)
        self.log.info(log_str)

        if resp is None:
            return self.app
        else:
            return resp


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)

    def req_resp_logger(app):
        return RequestResponseLogger(app, conf)
    return req_resp_logger
