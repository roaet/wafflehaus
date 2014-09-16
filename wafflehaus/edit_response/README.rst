========================
Edit Response Attributes
========================

The edit_response filter is designed to add or remove certain attributes from a response
that we may not want to show to our consumers.

Configuration
~~~~~~~~~~~~~

::

    [filter:edit_response]
    paste.filter_factory = wafflehaus.edit_response:filter_factory
    enabled = true

Optional Definitions

#. Filter names can be abitrary, but must match on resource and attrib key names ::

    filters = network port

#. Associated resource method and path ::

    network_resource = GET POST PUT /v2.0/networks
    port_resource = GET POST PUT /v2.0/ports

#. Associated attribute name (Defaults to delete, unless a value given below) ::

    network_key = bridge
    port_key = ipam_strategy

#. New value for attribute, if desired (if omitted, attribute is deleted) ::

    network_value = strawberry
    port_value = chocolate

Use Case
~~~~~~~~

This filter is useful if your api requests typically return data that may be harmful
if exposed to your customers. Alternatively, if you want to add data, this can also
be done.
