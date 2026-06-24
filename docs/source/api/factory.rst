`factory` module
=================

A module providing utilities for the abstract definition of interfaces to the tmQM-RDF ABox. It relies on Python's abc_ module to define an abstract ABox-subgraph class, implemented by the classes in the :doc:`assertions` and that can also be used to define custom interfaces.

.. _abc: https://docs.python.org/3/library/abc.html

.. autoclass:: tmqmrdfdata.factory.AbstractTmqmRDFABoxSubgraph
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__

.. autofunction:: tmqmrdfdata.factory.read_kgraph_file

.. autofunction:: tmqmrdfdata.factory.simple_tmqmrdf_abox_interface
