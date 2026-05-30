"""
A module dedicated to processing and referencing the terminology component of tmQM-RDF. 
It serves a dual purpose: it exposes the namespaces used in tmQM-RDF as 
[rdflib.Namespace](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace/) objects and provides 
a class that contains all the namespaces and URIs in the tmQM-RDF TBox as attributes, for accessible and quick referencing.

- Variables
  - For each prefix `<pfx>` used in tmQM-RDF, a variable `tmqmrdfdata.terminology.<pfx>` is defined as 
    an [rdflib.Namespace](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace/) instance.

Author: Luca Cibinel, ORCID: 0009-0009-1274-8327

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
import rdflib
import collections

cm = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/complex/")
cmT = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/complex/TMC/")
cmTp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/TMC/property/")
ds = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/")
dsC = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/complexes/")
dsG = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/graphs/")
dsL = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/datasets/ligands/")
lg = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/")
lgB = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/")
lgBp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/property/")
lgBr = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/reference/")
lgBrp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/bond/reference/property/")
lgC = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/")
lgCp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/property/")
lgCr = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/reference/")
lgCrp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/centre/reference/property/")
lgL = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/")
lgLp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/property/")
lgLr = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/")
lgLrm = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/motif/")
lgLro = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/occurrence/")
lgLrp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/ligand/reference/property/")
lgS = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/ligand/structure/")
ms = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/misc/")
nm = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/numerical/")
rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
tm = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/")
tmA = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/")
tmAp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/property/")
tmAr = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/reference/")
tmArp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/reference/property/")
tmB = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/")
tmBp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/property/")
tmBr = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/reference/")
tmBrp = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/bond/reference/property/")
tmS = rdflib.Namespace("https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/structure/")
xmls = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

class TmqmRDFTBoxSubgraph:
    """
    A convenience class designed to summarise the TBox of tmQM-RDF.

    Upon initialisation of [tmqmrdfdata.TmqmRDF](#-tmqmrdfdatatmqmrdf), this class is instantiated as an attribute of the main interface. 
    This class crawls across the knowledge graph collecting all the effective namespaces and URIs defined by the TBox. 
    This mechanism allows to avoid hardwiring the RDF/RDFS terms into the code and allows the package to adapt to 
    potential changes implemented in future versions of the knowledge graph.

    - **Attributes**:
        - `kgraph`: the [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) representation of the TBox.
        - `tmqmrdf`: the parent [tmqmrdfdata.TmqmRDF](#-tmqmrdfdatatmqmrdf) instance.
        - For each namespaxe `<pfx>` defined in tmQM-RDF, an attribute `.<pfx>` is defined. The value of the attribute 
          is a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) whose attributes are 
          the suffixes of the URIs within the namespace (those attributes evaluate to the 
          corresponding [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) objects).

    """

    def __init__(self, tmqmrdf):
        """    
        - **Parameters**:
            - `tmqmrdf`: the parent TmqmRDF instance.
        """
        self.tmqmrdf = tmqmrdf

        self.kgraph = rdflib.Graph()

        # Parse TBox rdf graphs
        for dir, _, files in os.walk(os.path.join(self.tmqmrdf.path, "terminology")):
            for f in files:
                if not f.endswith(".ttl"):
                    continue

                self.kgraph.parse(os.path.join(dir, f))

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
            

        # Convert namespaces in namedtuples
        ntpl = {
            nsname: collections.namedtuple(
                f"NS{nsname}",
                list(nsdata["members"].keys())
            )(**nsdata["members"])
            for nsname, nsdata in ns.items()
        }

        for nsname, obj in ntpl.items():
            self.__setattr__(nsname, obj)
