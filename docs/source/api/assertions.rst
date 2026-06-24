`assertions` module
===================

A module designed to handle the individual subgraphs of the tmQM-RDF ABox corresponding to TMCs, ligand species, metal centres, and elements. In addition to exposing the standard functionalities provided by rdflib_, the classes defined in this module allow 
to easily retrieve all the possible properties of these objects using a networkx_-like syntax.

.. _rdflib: https://rdflib.readthedocs.io/en/stable/
.. _networkx: https://networkx.org/en/

.. autoclass:: tmqmrdfdata.assertions.TmqmRDFABoxSubgraph
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__
   :exclude-members: name

   .. autoattribute:: tmqmrdfdata.assertions.TmqmRDFABoxSubgraph.name
      :no-value:

.. autoclass:: tmqmrdfdata.assertions.TMC
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__

.. autoclass:: tmqmrdfdata.assertions.Ligand
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__

.. autoclass:: tmqmrdfdata.assertions.Centre
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__

.. autoclass:: tmqmrdfdata.assertions.Element
   :members:
   :show-inheritance:
   :inherited-members:
   :special-members: __init__