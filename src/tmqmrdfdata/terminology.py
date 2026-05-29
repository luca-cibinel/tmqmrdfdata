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

class TmQMRDFTBoxSubgraph:

    def __init__(self, tmqmrdf):
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
