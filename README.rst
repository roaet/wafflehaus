==========
Wafflehaus
==========

Wafflehaus is a collection of WSGI middleware for OpenStack that adds
functionality with zero impact to code. 

Cloud providers of all sizes have problems dealing with business-requirements
of their cloud and diverging from upstream. By putting business logic into
middleware providers can create special cases without changing upstream code.

Not diverging from upstream is wonderful because:

* You do not need to handle merge conflicts
* The review process for wafflehaus is shorter especially if you fork it
* Although your requirement may not benefit OpenStack as a whole, it still fits
  in Wafflehaus

Beyond the above benefits, other benefits of using wafflehaus are:

* You gain access to plenty of predefined middlewares that can usually be
  configured to support your special case
* All of the middleware in wafflehaus are designed to be configured in the
  api-paste.ini file and thus can be distributed however you wish (puppet,
  chef, ansible)

Finally, although Wafflehaus was intended to work with OpenStack, it is
possible to use it in front of any WSGI compliant service.

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

Subprojects
-----------

In some situations it is impossible to completely ignore a dependency on a 
project. In those situations there are subprojects for those dependencies:

* `wafflehaus.neutron <http://github.com/roaet/wafflehaus.neutron>`_
* `wafflehaus.nova <http://github.com/roaet/wafflehaus.nova>`_

If a subproject is not listed here it may still exist. Also new ones can be
made at any time.
