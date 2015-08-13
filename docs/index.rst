.. pyrs-schema documentation master file, created by
   sphinx-quickstart on Wed Aug 12 19:44:15 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyrs-schema's documentation!
=======================================

This framework is the base part of pyrs microframework.
It's introduce the way to define schemas.
Main purpose is ensure json schema validation, json serialisation but
also possible to use it as part of ORM.

Example usage
-------------

.. code-block:: python

   from pyrs import schema

   class User(schema.Object):
       username = schema.String(required=True, minlen=3)
       password = schema.String(required=True, minlen=6)
       email = schema.Email()
       date_of_birth = schema.Date()

       class Attrs:
           additional=True

   user_schema = User()
   user = user_schema.loads(<jsonstring>)
   user_str = user_schema.dumps(user)


Contents:

.. toctree::
   :maxdepth: 2

   types

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

