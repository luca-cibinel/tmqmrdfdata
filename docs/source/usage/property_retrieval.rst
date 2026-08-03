Information Retrieval
=====================

As a general principle, each entity of interest in tmQM-RDF is described by a URI and a set of additional information.
The URI represents the object at the RDF level and serves as a unique identifier for the object. The additional information is a set of data regarding the object
that can be used in practice. The nature and the contents of such set depend on the entity, as different objects require different descriptions. As a rule of thumb, the following
principles can be used to determine how this set may look like:

- If an entity can be canonically identified via a symbol (e.g., the CSD code of a TMC, or the chemical symbol of an atom), that symbol and its URI representation will be available.
- If an entity can be canonically decomposed into smaller objects (e.g., a TMC can be decomposed into its ligands, or a chemical bond can be decomposed into its participating atoms), a list of the URIs of those objects will be available.
- If an entity can be endowed with properties, in the sense explained in [cibinel2026rdf]_, those properties (appropriately represented as python objects) can be made available upon the user's request.

The information set is encoded internally as a Python object (roughly equivalent to a pickle-safe version of a `collections.namedtuple`_ instance) and its content is acessible via Python's dot notation.

Retrieval Methods
-----------------

The following methods are available in the :doc:`../api/assertions` to retrieve the URI/information set pair for each possible entity of interest:

- :meth:`tmqmrdfdata.assertions.TMC.atoms` (provides: *symbol* and *properties*) |dagger|,
- :meth:`tmqmrdfdata.assertions.TMC.bonds` (provides: *decomposition* and *properties*) |dagger|,
- :meth:`tmqmrdfdata.assertions.TMC.centre` (provides: *symbol* and *decomposition*),
- :meth:`tmqmrdfdata.assertions.TMC.complex` (provides: *symbol*, *decomposition*, and *properties*),
- :meth:`tmqmrdfdata.assertions.TMC.lbonds` (provides: *decomposition*) |dagger|,
- :meth:`tmqmrdfdata.assertions.TMC.ligands` (provides: *symbol* and *decomposition*) |dagger|,
- :meth:`tmqmrdfdata.assertions.Ligand.species` (provides: *symbol* and *properties*).

The methods marked with |dagger| return a dictionary whose key-value pairs are the pair URI-information set described above.
The remaining methods will return, by default, the same pair in the form of a tuple, but the return type can be changed to a dictionary by passing ``as_tuple = False``.

Requesting Properties
---------------------

From an RDF/RFS perspective, the possible properties that can be encountered in tmQM-RDF are defined as RDFS classes belonging to an appropriate namespace.
For example, the property ``natural_atomic_charge`` of an atom instance, can be found in the ``tmAp`` namespace. The documentation of each data-retrieval method 
specifies the correct namespace it can retrieve, so there is no need to remeber the actual meaning of each prefix.

Methods that can retrieve these properties do so via the ``data`` parameter. This can accept either a single URI (represented as a string or as an `rdflib.term.URIRef`_ instance)
or a list of such objects. Each requested property will be stored in a homonym parameter of the information set object. The knwoledge graph representing the property is recursively traversed
and contracted into a Python object, whose attributes represent predicates applying to the corresponding URI term, and the value of these attributes are the recursive serialisation of the knowledge graph
ultimately representing the object of the predicate and its related assertions. [#containers]_

Due to this mechanism, the specific structure of each information set object depends on the specific RDF encoding of each individual property. Please refer to
[cibinel2026rdf]_ for additional information. Nonetheless, there are four specific attributes that are common to every property:

- ``type``: the URI of the RDFS class representing this property;
- ``reference``: the URI of the original dataset in the tmQM dataset series from which this property has been drawn;
- ``value``: the actual value of the property (depending on how this property is described, it can be a literal, an `rdflib.term.URIRef`_ object, or a recursively serialised object, as described above);
- ``alt``: since multiple properties in tmQM-RDF are reported in two different datasets (typically tmQM and tmQMg), one of the two entries is relabeled as "alternative" and assigned to the ``alt`` attibute. Its possible to specify which dataset should be regarded as the alternative via the ``alt`` parameter of the data retrieval method.

Referencing Properties
----------------------

In order to specify a property, its URI must be provided. It is not necessary, however, to manually write the entire URI, as `tmqmrdfdata <../index.rst>` provides two
convenient shortcuts:

- The :doc:`../api/terminology` possesses one attribute for each RDF namespace introduced in tmQM-RDF, encoded as an `rdflib.Namespace`_ object. Using the properties of these objects, it is possible to represent in Python the full URI of the term ``pfx:obj`` as ``pfx["obj"]``.
- The :attr:`tmqmrdfdata.TmqmRDF.tbox` attribute contains an instance of :class:`tmqmrdfdata.terminology.TmqmRDFTBoxSubgraph` which also encodes the namespaces as attributes, with the addition that all the terms defined in tmQM-RDF's TBox are made available via Python's dot notation. So, if ``ds`` is a ``tmqmrdfdata.TmqmRDF`` instance, the URI of ``pfx:obj`` is accessible as ``ds.tbox.pfx.obj``.

Example
-------

Suppose that we want to extract the natural atomic charge (``tmAp:natural_atomic_charge``) of the atoms composing the TMC identified as KCEYPT:

.. code-block:: python
    
    import tmqmrdfdata as tmrdf

    ds = tmrdf.TmqmRDF("path/to/tmQM-RDF")
    kceypt = ds.tmc("KCEYPT")

    atoms = kceypt.atoms(data = ds.tbox.tmAp.natural_atomic_charge)

    for uri, atom in atoms:
        print(
                f"Atom {uri}:\n\t- natural atomic charge = {atom.natural_atomic_charge.value}"
            )

By default, we will retrieve the natural atomic charge reported in tmQMg. The charge documented in tmQM (here treated as the "alternative") is available as:

.. code-block:: python
    
    for uri, atom in atoms:
        print(
                f"Atom {uri}:\n\t- natural atomic charge (tmQM) = {atom.natural_atomic_charge.alt.value}"
            )

Footnotes
---------

.. [#containers] The only exception to this scheme is represented by `RDFS Container Classes`_, which are serialised as lists and not as generic objects (the individual items inside the container are however still serialised as above).

References
----------

.. [cibinel2026rdf] Luca Cibinel, Trond Linjordet, Johan Pensar, David Balcells, Riccardo De Bin, Basil Ell; tmQM-RDF Data Set: A Knowledge Graph Representing Transition Metal Complexes. J. Chem. Inf. Model. 13 July 2026; 66 (13): 7524–7538. https://doi.org/10.1021/acs.jcim.6c01281

.. |dagger| unicode:: 0x2020

.. _collections.namedtuple: https://docs.python.org/3/library/collections.html#collections.namedtuple
.. _rdflib: https://pypi.org/project/rdflib/
.. _rdflib.Namespace: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace
.. _rdflib.term.URIRef: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef
.. _RDFS Container Classes: https://www.w3.org/TR/rdf-schema/#ch_containervocab