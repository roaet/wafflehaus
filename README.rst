==========
Wafflehaus
==========

Wafflehaus is a collection of WSGI middleware for OpenStack that adds
functionality with zero impact to code. 

Each middleware is lovingly called a waffle.

Cloud providers of all sizes have problems dealing with business-requirements
of their cloud and diverging from upstream. By putting business logic into
middleware providers can create special cases without changing upstream code.

Not diverging from upstream is wonderful because:

* You do not need to handle merge conflicts
* The review process for wafflehaus is shorter especially if you fork it
* Although your requirement may not benefit OpenStack as a whole, it still fits
  in Wafflehaus

Beyond the above benefits, other benefits of using wafflehaus are:

* You gain access to plenty of predefined waffles that can usually be
  configured to support your special case
* All of the waffles in wafflehaus are designed to be configured in the
  api-paste.ini file and thus can be distributed however you wish (puppet,
  chef, ansible)

Finally, although Wafflehaus was intended to work with OpenStack, it is
possible to use it in front of any WSGI compliant service.

Getting Help
------------

The official channel for wafflehaus support in on freenode in #wafflehaus. 

Using Wafflehaus
----------------

Using wafflehaus is simple! A stable version is available on pypi but you can
always install wafflehaus using pip+git. Modify your api-paste.ini to include
your waffle of choice and add the waffle where you wish in the composite
that defines your app.

Example using dns_filter::

    [composite:neutronapi_v2_0]
    use = call:neutron.auth:pipeline_factory
    noauth = dns_filter request_id catch_errors extensions neutronapiapp_v2_0
    keystone = dns_filter request_id catch_errors authtoken keystonecontext
               extensions neutronapiapp_v2_0

    # This is the waffle
    [filter:dns_filter]
    paste.filter_factory = wafflehaus.dns_filter.whitelist:filter_factory
    whitelist = mydomain.com
    # Uncomment the line below to activate the waffle
    # enabled = true

Then restart the service (or SIGHUP if it applies). If you have an error in
your configuration you'll see it in your logs very early, fix that and you'll
be rolling.

Note: All waffles are disabled until explicitly set to enabled with the
enabled = true configuration flag. This allows you to deploy a waffle without
concerns (beyond configuration being correct or not).

Current Deployment Quirks
~~~~~~~~~~~~~~~~~~~~~~~~~

Right now all the subprojects do not include wafflehaus in their requirements
file. This is because of weird quirks we have been happening while deploying
wafflehaus' subprojects. We are working to get those fixed but please do note:
the subprojects do require wafflehaus to be installed.

Contributing
------------

* Typical github-etiquette expected
* Conform to the guidelines below

Development Guidelines
~~~~~~~~~~~~~~~~~~~~~~

1. Provide a solution in its most shareable form
2. Add reusuable functionality to wafflehaus as a whole (see resource_filter)
3. Do not configure in code; configure from external files
4. Do not depend on specific OpenStack projects
5. If you must depend on a specific OpenStack project, look for the
   corresponding wafflehaus **subproject**
6. Each package should have a README.rst
7. Provide an example use-case of your middleware in the documentation
8. Do not raise exceptions, return them
9. Do not assume any other waffle exists if you can; document if you can't
10. Readable code is preferred over clever code

Subprojects
-----------

In some situations it is impossible to completely ignore a dependency on a 
project. In those situations there are subprojects for those dependencies:

* `wafflehaus.glance <http://github.com/roaet/wafflehaus.glance>`_
* `wafflehaus.neutron <http://github.com/roaet/wafflehaus.neutron>`_
* `wafflehaus.nova <http://github.com/roaet/wafflehaus.nova>`_

If a subproject is not listed here it may still exist. Also new ones can be
made at any time.
