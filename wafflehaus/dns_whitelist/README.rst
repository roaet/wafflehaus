DNS Whitelist
=============

DNS Whitelist provides a filter for WSGI applications by using namespace
resolution as a form of authentication. You provide a whitelisted domain list
and this filter will prevent all requests from continuing in the WSGI pipeline
that do not meet the requirements.

Tips
----

If the requesting IP does not have a valid DNS entry it will fail with a
warning in the logs. For aberrant requests this may cause some worry due to the
*warning* in the logs. It is highlighted for expected requests that are lacking
proper DNS settings.

Example Config
--------------

A basic configuration for normal use::

    [filter:dns_filter]
    paste.filter_factory = wafflehaus.dns_whitelist.dns_whitelist:filter_factory
    whitelist = mydomain.com

Example Positive Testing Config
-------------------------------

Will always pass the filter through but will provide the ability to see if the
filter is working::

    [filter:dns_filter]
    paste.filter_factory = wafflehaus.dns_whitelist.dns_whitelist:filter_factory
    whitelist = mydomain.com
    testing = true
    testing_remote_addr = 123.123.123.123 # a valid IP for whitelist

Example Negative Testing Config
-------------------------------

Will never pass the filter through so you can see how your service reacts when
a request is filtered::

    [filter:dns_filter]
    paste.filter_factory = wafflehaus.dns_whitelist.dns_whitelist:filter_factory
    whitelist = mydomain.com
    negative_testing = true
    testing_remote_addr = 123.123.123.123 # an invalid IP for whitelist
