`terminology` module
====================

A module dedicated to processing and referencing the terminology component of tmQM-RDF. 
It serves a dual purpose: it exposes the namespaces used in tmQM-RDF as 
`rdflib.Namespace`_ objects and defines a class that contains all the namespaces and URIs in the tmQM-RDF TBox as attributes, for accessible and quick referencing.

This module exposes the following variables:

- For each prefix `<pfx>` used in tmQM-RDF, a variable of the form`tmqmrdfdata.terminology.<pfx>` is defined as 
    an `rdflib.Namespace`_ instance.

.. _rdflib.Namespace: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace


.. autodata:: tmqmrdfdata.terminology.DEFAULT_NAMESPACES
    :no-value:

.. autodata:: tmqmrdfdata.terminology.DEFAULT_PREFIXES
    :no-value:

.. autoclass:: tmqmrdfdata.terminology.TmqmRDFTBoxSubgraph
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__