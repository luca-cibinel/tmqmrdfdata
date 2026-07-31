"""
A module dedicated to processing and referencing the terminology component of tmQM-RDF. 
It serves a dual purpose: it exposes the namespaces used in tmQM-RDF as 
`rdflib.Namespace`_ objects and defines a class that contains all the namespaces and URIs in the tmQM-RDF TBox as attributes, for accessible and quick referencing.

This module exposes the following variables:

- For each prefix `<pfx>` used in tmQM-RDF, a variable of the form`tmqmrdfdata.terminology.<pfx>` is defined as 
    an `rdflib.Namespace`_ instance.

Author: Luca Cibinel, ORCID: 0009-0009-1274-8327

.. _rdflib.Namespace: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace
---

MIT License

Copyright (c) 2026 Luca Cibinel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
import rdflib
import collections

DEFAULT_NAMESPACES = dict() #: A dictionary containing the prefixes defined in tmQM-RDF as keys and the corresponding `rdflib.Namespace`_ objects as values.
DEFAULT_NAMESPACES["cm"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/complex/")
DEFAULT_NAMESPACES["cmT"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/complex/TMC/")
DEFAULT_NAMESPACES["cmTp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/TMC/property/")
DEFAULT_NAMESPACES["ds"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/")
DEFAULT_NAMESPACES["dsC"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/complexes/")
DEFAULT_NAMESPACES["dsG"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/graphs/")
DEFAULT_NAMESPACES["dsL"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/ligands/")
DEFAULT_NAMESPACES["lg"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/")
DEFAULT_NAMESPACES["lgB"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/")
DEFAULT_NAMESPACES["lgBp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/property/")
DEFAULT_NAMESPACES["lgBr"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/reference/")
DEFAULT_NAMESPACES["lgBrp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/reference/property/")
DEFAULT_NAMESPACES["lgC"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/")
DEFAULT_NAMESPACES["lgCp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/property/")
DEFAULT_NAMESPACES["lgCr"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/reference/")
DEFAULT_NAMESPACES["lgCrp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/reference/property/")
DEFAULT_NAMESPACES["lgL"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/")
DEFAULT_NAMESPACES["lgLp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/property/")
DEFAULT_NAMESPACES["lgLr"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/")
DEFAULT_NAMESPACES["lgLrm"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/motif/")
DEFAULT_NAMESPACES["lgLro"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/occurrence/")
DEFAULT_NAMESPACES["lgLrp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/property/")
DEFAULT_NAMESPACES["lgS"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/structure/")
DEFAULT_NAMESPACES["ms"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/misc/")
DEFAULT_NAMESPACES["nm"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/numerical/")
DEFAULT_NAMESPACES["rdf"] = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEFAULT_NAMESPACES["rdfs"] = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
DEFAULT_NAMESPACES["tm"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/")
DEFAULT_NAMESPACES["tmA"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/")
DEFAULT_NAMESPACES["tmAp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/property/")
DEFAULT_NAMESPACES["tmAr"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/reference/")
DEFAULT_NAMESPACES["tmArp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/reference/property/")
DEFAULT_NAMESPACES["tmB"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/")
DEFAULT_NAMESPACES["tmBp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/property/")
DEFAULT_NAMESPACES["tmBr"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/reference/")
DEFAULT_NAMESPACES["tmBrp"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/reference/property/")
DEFAULT_NAMESPACES["tmS"] = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/structure/")
DEFAULT_NAMESPACES["xmls"] = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

DEFAULT_PREFIXES = dict() #: The inverse of :data:`DEFAULT_NAMESPACES`
_this = sys.modules[__name__]
for pfx, ns in DEFAULT_NAMESPACES.items():
    setattr(_this, pfx, ns)
    DEFAULT_PREFIXES[ns] = pfx

class _RuntimeNamespace:

    def __init__(self, ns, content):
        self._internal_ns_repr = ns

        for symbol, uri in content.items():
            self.__setattr__(symbol, uri)

    def __getitem__(self, key):
        return self._internal_ns_repr[key]

    def __repr__(self):
        return f"<src.tmqmrdfdata.terminology._RuntimeNamespace(ns = {self._internal_ns_repr})>"

    def __str__(self):
        return str(self._internal_ns_repr)

class TmqmRDFTBoxSubgraph:
    """
    A convenience class designed to summarise the TBox of tmQM-RDF.

    Upon initialisation of :class:`tmqmrdfdata.TmqmRDF`, this class is instantiated as an attribute of the main interface. 
    This class crawls across the knowledge graph collecting all the effective namespaces and URIs defined by the TBox. 
    This mechanism allows to avoid hardwiring the RDF/RDFS terms into the code and allows the package to adapt to 
    potential changes implemented in future versions of the knowledge graph.

    The class has the following attributes:
    
    - :attr:`kgraph`: The `rdflib.Graph`_ representation of the TBox.
    - :attr:`tmqmrdf`: The parent :class:`tmqmrdfdata.TmqmRDF` instance.
    - For each namespaxe `<pfx>` defined in tmQM-RDF, an attribute `.<pfx>` is defined. The value of the attribute 
      is a pickle-safe runtime initiated objects whose attributes are 
      the suffixes of the URIs within the namespace. Each attribute evaluates to the 
      corresponding `rdflib.term.URIRef`_ objects defined in the TBox. The objects also implement the same
      __getitem__ behaviour as `rdflib.Namespace`_. The namespace URI is accessible via ``str()``, which can then
      be used as a key for :attr:`tmqmrdfdata.terminology.DEFAULT_PREFIXES`.

    .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
    .. _rdflib.term.URIRef: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef

    """

    def __init__(self, tmqmrdf):
        """    
        :param tmqmrdf: The parent :class:`tmqmrdfdata.TmqmRDF` instance.
        """

        self.tmqmrdf = tmqmrdf
        """The parent :class:`tmqmrdfdata.TmqmRDF` instance."""

        self.kgraph = rdflib.Graph()
        """ The `rdflib.Graph`_ representation of the TBox."""

        # Parse TBox rdf graphs
        for dir, _, files in os.walk(os.path.join(self.tmqmrdf.path, "terminology")):
            for f in files:
                if f.split(".")[-1] not in (list(rdflib.util.SUFFIX_FORMAT_MAP) + ["hdt"]):
                    continue

                self.kgraph += self.tmqmrdf._read_kgraph(os.path.join(dir, f))

        for pfx, ns in DEFAULT_NAMESPACES.items():
            self.kgraph.bind(pfx, ns, True, True)

        # Identify namespaces and related URIs
        ns = {
            nsname: {
                "ns": rdflib.Namespace(nsuri),
                "members": {}
            }
            for nsname, nsuri in self.kgraph.namespaces()
        }

        for suri in self.kgraph.subjects():
            nsname, _, suffix = self.kgraph.compute_qname(suri)

            ns[nsname]["members"][suffix] = ns[nsname]["ns"][suffix]
            

        # Convert namespaces into objects
        ntpl = {
            nsname : _RuntimeNamespace(
                nsdata["ns"],
                nsdata["members"]
            )
            for nsname, nsdata in ns.items() if len(nsdata["members"]) > 0
        }

        for nsname, obj in ntpl.items():
            self.__setattr__(nsname, obj)
