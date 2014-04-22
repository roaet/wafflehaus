DNS Filtering
=============

The DNS filter package provides a collection of WSGI filters that are intended
to be used with Paste.deploy but may also be used stand-alone.

DNS Whitelist
-------------

DNS Whitelist provides a filter for WSGI applications by using namespace
resolution as a form of authentication. You provide a whitelisted domain list
and this filter will reject all requests from continuing in the WSGI pipeline
that do not meet the requirements.

Use-Case
~~~~~~~~

Having no desire to authenticate between service-boundaries for performance
reasons, one can ensure that a service is serving requests from trusted
networks.

Tips
~~~~

If the requesting IP does not have a valid DNS entry it will fail with a
warning in the logs. For aberrant requests this may cause some worry due to the
*warning* in the logs. It is highlighted for expected requests that are lacking
proper DNS settings.

Example Config
~~~~~~~~~~~~~~

A basic configuration for normal use::

    [filter:dns_filter]
    paste.filter_factory = wafflehaus.dns_filter.whitelist:filter_factory
    whitelist = mydomain.com

This will pass any request that resolves to a domain that ends with
*mydomain.com* (such as wwww.mydomain.com, mydomain.com,
secure.sub.mydomain.com, etc.).

The whitelist configuration option is a space delimited list.

Example Positive Testing Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Will always pass the filter through but will provide the ability to see if the
filter is working::

    [filter:dns_filter]
    paste.filter_factory = wafflehaus.dns_filter.whitelist:filter_factory
    whitelist = mydomain.com random.org
    testing = true
    testing_remote_addr = 123.123.123.123 # a valid IP for whitelist

Dealing with Load Balanced Requests with X-Forwarded-For
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your service is behind a load balancer, as most cloudy things are, you will
need to ensure that the load balancer provides an X-Forwarded-For header to
this service.

If your service is behind a load balancer and you do not desire to read the
X-Forwarded-For header, you may set the configuration option `ignore_forwarded`
to true and it will not use that header.

This filter will use the first IP address in the X-Forwarded-For list.
