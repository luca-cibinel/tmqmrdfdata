.. tmqmrdfdata documentation master file, created by
   sphinx-quickstart on Tue Jun 23 15:41:35 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

``tmqmrdfdata`` documentation
=============================

``tmqmrdfdata`` is an rdflib_-based Python package designed to support and facilitate the interaction with `tmQM-RDF (a Knowledge Graph Representing Transition Metal Complexes) <https://github.com/luca-cibinel/tmQM-RDF>`_.
Amongst its main functionalities, the package allows to:
  
- easily download the data from the dedicated GitHub repository;
- access specific subgraphs;
- retrieve the available quantitative and qualitative properties in a Python-friendly format.

.. _rdflib: https://pypi.org/project/rdflib/

Installation
------------

The package may be installed using ``pip``:

.. code-block:: bash

   pip install tmqmrdfdata


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage/getting_started
   usage/lookup
   usage/property_retrieval.rst
   examples/fetch_zirconium_hepta5

.. toctree::
   :maxdepth: 2
   :caption: API reference:

   api/download
   api/assertions
   api/terminology

