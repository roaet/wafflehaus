========================
Edit Response Attributes
========================

The edit_response filter is designed to add or remove certain attributes from a response
that we may not want to show to our consumers.

Using the foreach option you can choose to selectively remove items from the
response if they pass or fail simple criteria.

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

Using foreach
~~~~~~~~~~~~~

Foreach can be used when the response is expected to be a list of dicts.

::

    [filter:hide_extensions]
    paste.filter_factory = wafflehaus.edit_response:filter_factory
    enabled = true
    filters = extensions
    extensions_resource = GET /v2.0/extensions{.format}
    extensions_key = extensions
    extensions_value = foreach:keep_if:alias=security-group

In the above configuration example if the alias attribute of an element of the
list is equal to security-group. Any other elements will be dropped.

Another element can be allowed if the criteria is expanded.

::

    extensions_value = foreach:keep_if:alias=security-group,alias=quotas

It is also possible to drop if the criteria is met by using drop_if instead of
keep_if.

Use Case
~~~~~~~~

This filter is useful if your api requests typically return data that may be harmful
if exposed to your customers. Alternatively, if you want to add data, this can also
be done.
