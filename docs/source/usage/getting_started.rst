Getting started
===============

Installation
------------
To begin, install the package using `pip`:

.. code-block:: bash
   
   pip install tmqmrdfdata

Downloading the knowledge graph
-------------------------------

The tmQM-RDF knowledge graph can be downloaded directly from Python via the following code:

.. code-block:: python
   
   from tmqmrdfdata import download_tmQM_RDF_knowledge_graph

   download_tmQM_RDF_knowledge_graph(
        dir = "data/",
        version = "latest"
   )

This will download the latest available version of tmQM-RDF into the directory ``data/``. Supposing that the latest version is version 1.0, the finaly directory tree will look like this:

.. code-block:: bash
   
   data/
   └── tmQM-RDF-v1.0
       ├── assertions/
       │   └── ...
       └── terminology/
           └──  ...

It is possible to download a specific version of tmQM-RDF by changing the ``version`` parameter. This parameter takes in input a string representing the *exact* version number to retrieve (without any leading prefix, e.g., to download the version v1.0.1, you must type ``version = "1.0.1"``).

HDT Format
^^^^^^^^^^

By default, tmQM-RDF is stored in `turtle`_ format, which is human-readable, but not particularly efficient when it comes to extensive tasks. One alternative
is to use the `HDT`_ format. Although not human-readable, it allows for increased efficiency both in terms of memory and time. An HDT-equivalent version of tmQM-RDF
can be downloaded with the same code shown above, with the addition of the ``hdt_format = True`` argument.

.. _turtle: https://www.w3.org/TR/turtle/
.. _HDT: https://www.w3.org/TR/turtle/

Interfacing with the data
-------------------------
Once the data has been downloaded, the main interface can be instantiated:

.. code-block:: python
   
   from tmqmrdfdata import TmqmRDF

   interface = TmqmRDF("data/")

This will initialise a dictionary-like object that can retrieve information from the knowledge graph. Upon instantiation, only the *terminology component* (or *TBox*) is immediately available, whereas any part of the *assertion component* (or *ABox*) will have to be explicitly retrieved first.

Accessing the TBox
^^^^^^^^^^^^^^^^^^
The TBox contains the definition of all the terms used in the knowledge graphs. A wrapper of this part of the knowledge graph is available in the attribute ``interface.tbox``. See the :doc:`related documentation <../api/terminology>`.


Accessing the ABox
^^^^^^^^^^^^^^^^^^
Subgraphs regarding assertions on specific TMCs, ligand species, metal centres, or chemical element are retrieved using the method ``interface.fetch``:

.. code-block:: python

   interface.fetch(tmcs = ["KCEYPT", "ABEVAH"], ligands = ["ligand1-0"])

Now the interface has access to the subgraphs related to the TMCs *KCEYPT* and *ABEVAH* and the ligand species *ligand1-0* (according to the indexes used in `tmQMg-L`_).

These can be now accessed explicitly as follows:

.. code-block:: python

   kceypt = interface["TMC", "KCEYPT"]
   lig1_0 = interface["ligand", "ligand1-0"]

Both *kceypt* and *lig1-0* are instances of (subclasses) of :class:`tmqmrdfdata.assertions.TmqmRDFABoxSubgraph`. Metal centres and elements can be accessed with the notation ``interface["centre", ...]`` and ``interface["element", ...]`` respectively.

Retrieval and access can be performed more conveniently using the methods ``.tmc``, ``.ligand``, ``.centre``, or ``.element``. For instance, the code

.. code-block:: python

   kceypt = interface.tmc("KCEYPT")
   lig1_0 = interface.ligand("ligand1-0")

is equivalent to

.. code-block:: python

   interface.fetch(tmcs = ["KCEYPT"], ligands = ["ligand1-0"])
   kceypt = interface["TMC", "KCEYPT"]
   lig1_0 = interface["ligand", "ligand1-0"]

Property retrieval
^^^^^^^^^^^^^^^^^^

.. note:: This topic is treated in detail in :doc:`/usage/property_retrieval`.

Within tmQM-RDF, atoms, atomic bonds, ligand species, and whole complexes are endowed with properties, which can be accessed from the corresponding knowledge graph. 

For example, if you wish to retrieve the natural atomic charge of the atoms of KCEYPT you can use the following code:

.. code-block:: python

   from tmqmrdfdata.terminology import tmAp

   atoms_w_charge = kceypt.atoms(data = tmAp["natural_atomic_charge"])

Notice that the property had to be specified using ``tmAp["natural_atomic_charge"]``. Let's break this symbol down:

- ``tmAp``: this is a variable introduced in the :doc:`../api/terminology`. It is an `rdflib.Namespace`_ encoding the namespace
  
  .. code-block:: bash

      <https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/property/>.

- ``tmAp["natural_atomic_charge"]`` produces the URI
    
  .. code-block:: bash

    <https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/property/natural_atomic_charge>,
    
  which is the URI that tmQM-RDF uses to denote the natural atomic charge property of atoms.

If you now want to inspect the result, you will have to go through a dictionary where the keys are the URIs of the atoms of KCEYPT whereas the values are Python objects mirroring the structure of the RDF graph describing the property. See :doc:`/usage/property_retrieval` and the documentation of the :doc:`../api/assertions` for information on how this mirroring is constructed.
For now, let's just inspect the first entry of this dictionary:

.. code-block:: python

   atom, atom_data = next(iter(atoms_w_charge.items()))

   print(atom)
   # >>> https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/KCEYPT_Pt_0

   print(atom_data.natural_atomic_charge.value)
   # >>> 0.73094

Notice that, regardless of whether and which properties you request, ``atom_data`` will always have the ``symbol`` attribute, containing the chemical symbol of the atom:

.. code-block:: python

   print(atom_data.symbol)
   # >>> https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/reference/Pt


Advanced querying
^^^^^^^^^^^^^^^^^
If you need to perform more advanced queries, you can always rely on `rdflib`_'s own machinery. You can access the rdflib's representation of the RDF graph via the attribute ``.kgraph`` of :class:`tmqmrdfdata.assertions.TmqmRDFABoxSubgraph`.

Visualising TMCs
^^^^^^^^^^^^^^^^
TMC-related subgraphs posses a unique method, that allows to visualise their molecular structure using `graphviz`_:

.. code-block:: python

   kceypt.view()

.. image:: https://github.com/luca-cibinel/tmqmrdfdata/blob/main/kceypt.png?raw=true
   :alt: Graphical representation of the TMC KCEYPT

Contact
-------
For any questions related to the package, contact Luca Cibinel: `https://orcid.org/0009-0009-1274-8327 <https://orcid.org/0009-0009-1274-8327>`_.

For questions regarding tmQM-RDF, please check the `tmQM-RDF contact info <https://www.integreat.no/research/rdf/tmqm-rdf-dataset/>`_.

.. _tmQMg-L: https://github.com/uiocompcat/tmQMg-L
.. _rdflib.Namespace: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace
.. _collections.namedtuple: https://docs.python.org/3/library/collections.html#collections.namedtuple
.. _rdflib: https://pypi.org/project/rdflib/
.. _graphviz: https://graphviz.readthedocs.io/en/stable/