Online File Lookup
==================

Sometimes, a quick glance at the source .ttl file could be more useful or interesting than exploring the data using the main APIs. This is due to the human-readable approach adopted during the creation of tmQM-RDF.
However, if the .hdt format is chosen, the .ttl files are not immediately available on your local machine, which means that you would either need to download another copy of the dataset (which can be particularly memory-intensive), or to navigate the `GitHub repository`_ looking for your specific target.

For this reason, the package provides a utility lookup feature that allows you to open up any .ttl file on your default browser directly from Python.

There are two different types of engines available:

- The global engine :attr:`tmqmrdfdata.no`;
- The local :attr:`.no` attribute of :class:`tmqmrdfdata.TmqmRDF`.

The main difference is that the latter already has access to the dataset's version number, hence you don't need to specify it in your query.

.. _GitHub repository: https://github.com/luca-cibinel/tmQM-RDF-archive/

Querying the Lookup Engine Using a String
-----------------------------------------

If ``L`` is your chosen lookup engine, a string-based query will have the following syntax:

.. code-block:: python

    L // "<version>/<TMC|ligand|centre|element>/<symbol>" # For querying the ABox
    L // "<version>/<namespace prefix>" # For querying the TBox

If ``L`` is a local engine, the component ``<version>/`` must be omitted.

Querying the Lookup Engine Using an Object
------------------------------------------

Instances of :class:`tmqmrdfdata.assertions.TmqmRDFABoxSubgraph` and `rdflib.Namespace`_ can also be used as query parameters. Since the information needed to locate the corresponding .ttl file can be programmatically extracted from these objects, a query can be executed using the sole syntax

.. code-block:: python

    L // obj

where ``L`` is the lookup engine and ``obj`` is the object instance. Note that, since `rdflib.Namespace`_ objects do not expose a pointer to the current instance of :class:`tmqmrdfdata.TmqmRDF`, they can only be used with local lookup engines. Instances of :class:`tmqmrdfdata.assertions.TmqmRDFABoxSubgraph`, on the other hand, can always be used as query parameters.

.. _rdflib.Namespace: https://rdflib.readthedocs.io/en/7.1.1/apidocs/rdflib.namespace.html#rdflib.namespace.Namespace