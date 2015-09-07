=========
Changelog
=========

The [!] sign marks the incompatible changes.

0.8
---

This release aim to improve the usability and flexibility. The declared schema
easily perambulate through with ``parent`` and ``root``. This are set on any
child schema **after** the schema initialised. This improvement helps to build
complex schemas, complex dependency without context. You can also introduce
special behaviour like ``dialect`` which is any time gets its value from the
top level schema.


Features
~~~~~~~~
 * Add ``logger`` to Schema
 * ``Any`` type introduced
 * Got rid of context argument
 * The get_jsonschema gives back a Wrapper which contains the schema object
   itself as ``origin`` attribute
 * Default value handling
 * Custom constraints introduced 
 * Mixin introduced to extend the functionality in any 3rd party module
 * Make available the ``parent`` and ``root`` in any Schema

Fixes
~~~~~
 * The excluded fields will be no shown up in the result

Minor changes
~~~~~~~~~~~~~
 * ``include`` has been renamed to ``exclusive`` [!]
 * ``dialect`` introduced as Schema field
 * Using the class rather than instance of Schema is not supported [!]
 * Password field introduced
 * Email field introduced
 * Version field introduced (future changes possible!)

0.7.3
-----

Fixes
~~~~~

 * Fix JSONReader / Form reader regarding dict input, dict schema

0.7.2
-----

Fixes
~~~~~

 * Get rid of the validation on FormReader

0.7.1
-----

Minor modifications
~~~~~~~~~~~~~~~~~~~

 * ``exceptions.*`` also imported in the ``pyrs.schema``

0.7
---

This release a major release with lots of modification on API.
One of the main concept is decouple responsibilities of schema, means
serialisation, deserialisation, validation. Regarding this I removed the
``load``, ``dump``, ``validate`` functions from schema. Also make possible the
further improvement the ``get_schema`` renamed to ``get_jsonschema``.

Major improvements
~~~~~~~~~~~~~~~~~~

 * ``JSONSchemaValidator`` introduced
 * ``JSONReader`` introduced
 * ``JSONFormReader`` introduced
 * ``JSONWriter`` introduced
 * ``validate`` removed from ``Schema`` (and the whole validation) [!]
 * ``load`` removed from ``Schema`` [!]
 * ``dump`` removed from ``Schema`` [!]
 * ``to_dict`` renamed to ``to_raw`` [!]
 * ``get_schema`` renamed to ``get_jsonschema`` [!]
 * Changed to MIT license

Minor modifications
~~~~~~~~~~~~~~~~~~~

 * ``ValidationErrors`` introduced and has became the unified umbrella error
 * ``SchemaWriter`` and ``JSONSchemaWriter`` introduced
 * ``JSONSchemaDictValidator`` introduced (for dict based schemas)
 * Cover document changed regarding the new API
 * Number types functionality extended
 * String type functionality extended
 * More tests for date and time related types
 * Doc and test removed from build
 * Changelog introduced

