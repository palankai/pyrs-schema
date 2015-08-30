=========
Changelog
=========

The [!] sign marks the incompatible changes.

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

