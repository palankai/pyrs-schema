================================
MicroService framework :: Schema
================================

.. image:: https://travis-ci.org/palankai/pyrs-schema.svg?branch=master
       :target: https://travis-ci.org/palankai/pyrs-schema

.. image:: https://coveralls.io/repos/palankai/pyrs-schema/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/palankai/pyrs-schema?branch=master

.. image:: https://readthedocs.org/projects/pyrs-schema/badge/?version=stable
   :target: http://pyrs-schema.readthedocs.org/en/stable/
   :alt: Documentation Status

Project hompage: `<https://github.com/palankai/pyrs-schema>`_

Documentation: `<http://pyrs-schema.readthedocs.org/>`_

What is this package for
------------------------

I've used different python frameworks for data serialisation many times. Mostly
when I had to implement an API for my work. I felt many times those frameworks
did good job but not extensible enough.
Also writing easily an API which is satisfy every expectations of projects,
without coupled restrictions sometimes really hard.

Features
--------
- Easy schema definition
- Schema validation
- Decoupled serialisation
- Extensibe API

Installation
------------

The code is tested with python 2.7, 3.3, 3.4.

.. code:: bash

   $ pip install pyrs-schema

Dependencies
------------

See requirements.txt. But The goal is less dependency as possible. The main
dependency is the 
`Python JSONSchema <https://pypi.python.org/pypi/jsonschema>`_
The validation is using that package.

Notice that even it's a JSON schema validator this work still can be used
for any (compatible) schema validation.

Important caveats
-----------------

This code is in beta version. I working hard on write stable as possible API in
the first place but while this code in 0.x version you should expect some major
modification on the API.

The ecosystem
-------------

This work is part of `pyrs framework <https://github.com/palankai/pyrs>`_.
The complete framework follow the same intention to implement flexible
solution.

Contribution
------------

I really welcome any comments!
I would be happy if you fork my code or create pull requests.
I've already really strong opinions what I want to achieve and how, though any
help would be welcomed.

Feel free drop a message to me!
