==============
Payload Filter
==============

The payload filter is a collection of middleware that allows an admin to
analyze the contents of the request body and modify it based on configurations.
Each payload filter provides specific capabilities to ease configuration:

- **unset_key** : will look in the body for a key and, if unset, set the value

Configuration of each payload filter is described below.

unset_key
---------

The unset_key filter will check the body for a key and if it doesn't exist it
will create the key in the body and set it to some configured value. This 
middleware provides support for simple JSON objects and complex JSON objects.

Simple::

    {"widget": { "name": "foo"}}

Complex::

    {"widget": { "name": "foo", "sub": { "name": "bar"}}}

As well as JSON objects that contain lists::

    {"widgets": [{"name": "1"},{"name": "2"}]}

It does not currently support XML.

Use Case
~~~~~~~~

As defined in the `subnet create api docs <http://docs.openstack.org/api/openstack-network/2.0/content/POST_os-subnets-v2_createSubnet_v2.0_subnets_subnets.html>`_
if the gateway_ip is not specified then OpenStack networking will allocate an
address for the gateway on the subnet and make it a default route.

If you are attempting to create a network and you do not wish to have a
default route assigned to your subnet then you will need to explicitly set
gateway_ip = null. This is inconvenient and this middleware can set should the
attribute not exist.

Special Syntax
~~~~~~~~~~~~~~

The configuration of what key and value to set that key as is a 
comma-separated list of tuples. The tuples have two sections:

- **value** which is after an equal sign, =
- **path** which is a colon-separated list, :

Value may be set to anything but some strings have special meaning:

- **null** will translate to python None which will be interpreted as JSON null
  but the key *will* exist in the body

Configuration
~~~~~~~~~~~~~

::

    [filter:default_payload]
    paste.filter_factory = wafflehaus.payload_filter.unset_key:filter_factory
    resource = POST /v2.0/subnets
    defaults = subnet:gateway_ip=null
    enabled = true

The above sample configuration does the following:

- this middleware will activate only on POST to /v2.0/subnets resource
- this middleware will look for a subnet object in JSON and if it does not have
  a gateway_ip attribute it will set it to null

The above sample configuration *does not* do the following:

- it will not handle bulk versions of the resource 'subnet'

To handle bulk support of a resource a second tuple must be added::

    defaults = subnet:gateway_ip=null, subnets:gateway_ip=null

If it is desired to support bulk with a single configuration (subnet also will
catch subnets) then it is possible but not currently developed.

Possible Errors
~~~~~~~~~~~~~~~

The unset_key middleware is not defined to produce any errors.
