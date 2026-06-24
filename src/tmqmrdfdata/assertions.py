"""
A module designed to handle the individual subgraphs of the tmQM-RDF ABox corresponding to TMCs, 
ligand species, metal centres, and elements. In addition to exposing the standard functionalities 
provided by rdflib_, the classes defined in this module allow 
to easily retrieve all the possible properties of these objects using a networkx_-like syntax.

Author: Luca Cibinel, ORCID: 0009-0009-1274-8327

.. _rdflib: https://rdflib.readthedocs.io/en/stable/
.. _networkx: https://networkx.org/en/

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

from . import terminology
from . import factory

from rdflib import container
from pathlib import Path

import collections
import tempfile
import graphviz
import rdflib
import re
import os

"""
Dictionary of the PubChem CPK color palette, derived from:
    https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV?response_type=save&response_basename=PubChemElements_all
"""
_PubChemCPKColors = {
    'H': 'FFFFFF',
    'He': 'D9FFFF',
    'Li': 'CC80FF',
    'Be': 'C2FF00',
    'B': 'FFB5B5',
    'C': '909090',
    'N': '3050F8',
    'O': 'FF0D0D',
    'F': '90E050',
    'Ne': 'B3E3F5',
    'Na': 'AB5CF2',
    'Mg': '8AFF00',
    'Al': 'BFA6A6',
    'Si': 'F0C8A0',
    'P': 'FF8000',
    'S': 'FFFF30',
    'Cl': '1FF01F',
    'Ar': '80D1E3',
    'K': '8F40D4',
    'Ca': '3DFF00',
    'Sc': 'E6E6E6',
    'Ti': 'BFC2C7',
    'V': 'A6A6AB',
    'Cr': '8A99C7',
    'Mn': '9C7AC7',
    'Fe': 'E06633',
    'Co': 'F090A0',
    'Ni': '50D050',
    'Cu': 'C88033',
    'Zn': '7D80B0',
    'Ga': 'C28F8F',
    'Ge': '668F8F',
    'As': 'BD80E3',
    'Se': 'FFA100',
    'Br': 'A62929',
    'Kr': '5CB8D1',
    'Rb': '702EB0',
    'Sr': '00FF00',
    'Y': '94FFFF',
    'Zr': '94E0E0',
    'Nb': '73C2C9',
    'Mo': '54B5B5',
    'Tc': '3B9E9E',
    'Ru': '248F8F',
    'Rh': '0A7D8C',
    'Pd': 'f78bb2',
    'Ag': 'C0C0C0',
    'Cd': 'FFD98F',
    'In': 'A67573',
    'Sn': '668080',
    'Sb': '9E63B5',
    'Te': 'D47A00',
    'I': '940094',
    'Xe': '429EB0',
    'Cs': '57178F',
    'Ba': '00C900',
    'La': '70D4FF',
    'Ce': 'FFFFC7',
    'Pr': 'D9FFC7',
    'Nd': 'C7FFC7',
    'Pm': 'A3FFC7',
    'Sm': '8FFFC7',
    'Eu': '61FFC7',
    'Gd': '45FFC7',
    'Tb': '30FFC7',
    'Dy': '1FFFC7',
    'Ho': '00FF9C',
    'Er': 'f78bb2',
    'Tm': '00D452',
    'Yb': '00BF38',
    'Lu': '00AB24',
    'Hf': '4DC2FF',
    'Ta': '4DA6FF',
    'W': '2194D6',
    'Re': '267DAB',
    'Os': '266696',
    'Ir': '175487',
    'Pt': 'D0D0E0',
    'Au': 'FFD123',
    'Hg': 'B8B8D0',
    'Tl': 'A6544D',
    'Pb': '575961',
    'Bi': '9E4FB5',
    'Po': 'AB5C00',
    'At': '754F45',
    'Rn': '428296',
    'Fr': '420066',
    'Ra': '007D00',
    'Ac': '70ABFA',
    'Th': '00BAFF',
    'Pa': '00A1FF',
    'U': '008FFF',
    'Np': '0080FF',
    'Pu': '006BFF',
    'Am': '545CF2',
    'Cm': '785CE3',
    'Bk': '8A4FE3',
    'Cf': 'A136D4',
    'Es': 'B31FD4',
    'Fm': 'B31FBA',
    'Md': 'B30DA6',
    'No': 'BD0D87',
    'Lr': 'C70066',
    'Rf': 'CC0059',
    'Db': 'D1004F',
    'Sg': 'D90045',
    'Bh': 'E00038',
    'Hs': 'E6002E',
    'Mt': 'EB0026',
    'Ds': 'f78bb2',
    'Rg': 'f78bb2',
    'Cn': 'f78bb2',
    'Nh': 'f78bb2',
    'Fl': 'f78bb2',
    'Mc': 'f78bb2',
    'Lv': 'f78bb2',
    'Ts': 'f78bb2',
    'Og': 'f78bb2'
}

class _BNCrawler:
    """
    A utility class that performs a DFS traversal only along edges whose start and/or end is a blank node.

    It also allows to filter/highlight certain nodes which match the pattern
        ?x :p :o
    for pre-specified :p and :o (e.g. :p = rdf:type, :o \in [set of properties]). These nodes will be retained and
    highlighted as 'attributes' named after :o
    """

    class _BNTraversal:
        """
        A utility class that represents the traversal performed by a BNCrawler.
        This class offers utilities to contract certain branches (rooted in the nodes that
        matched the given filters) of the traversal into (nested) named tuples
        """

        def __init__(self, crawler, closure, path, filtered_bns, name):
            """
            - Parameters:
                - crawler: the BNCrawler
                - closure: the nodes found by the DFS traversal
                - path: a dictionary of the form {node: [nodes reached from node]}
                - filtered_bns: the blank nodes that mathced the given filter
                - a name for the collapsed branches
            """
            self.crawler = crawler
            self.closure = closure
            self.path = path
            self.filtered_bns = filtered_bns
            self.name = name

        def contract(self, defaults, alt, **attribute_values):
            """
            Contract the whole traversal into a named tuple whose attributes correspond to the blank nodes that matched the filter
            plus the additional attributes.
            Sortes collisions (i.e., nodes that satisfy the filter with the same :p and :o but have different :reference) by
            demoting one of the two as 'alt' (alternative)

            - Parameters:
                - defaults: a list of parameters that the contracted branches should have
                    regardless of the predicates that apply to the filtered blank nodes
                - alt: which dataset is the alternative
                - **attribute_values: the user-provided values of the additional attributes
            """
            branches = [
                self.contract_branch(bn, defaults) for bn in self.filtered_bns
            ]

            # Handle collisions
            contractions = {}

            for b in branches:
                b_type = re.sub(r"\W", "/", b.type).split("/")[-1]

                if b_type in contractions:
                    stored_ref = contractions[b_type].reference.split("/")[-1]
                    
                    b_alt = contractions[b_type] if stored_ref == alt else b
                    b_main = contractions[b_type] if stored_ref != alt else b

                    _Entry = b.__class__
                    args = [*b_main]
                    args[-1] = b_alt # last argument of _Entry is "alt"

                    contractions[b_type] = _Entry(*args)
                    continue

                contractions[b_type] = b
            
            # Merge into a named tuple
            return self.crawler.Category(**{
                **attribute_values,
                **contractions
            })

        def contract_branch(self, bn, defaults = [], counter = 0):
            """
            Recursively contract a branch rooted at bn into a named tuple (or a list if predicates of the form _nnn are found,
            i.e., if the blank node is a container).

            - Parameters:
                - bn: the root
                - defaults: a list of default attributes to insert into the tuple regardless of which predicates apply to bn
                - counter: a counter representing how deep into the nesting we have gone
            """
            if not isinstance(bn, rdflib.term.BNode):
                return bn.toPython() if isinstance(bn, rdflib.term.Literal) else bn

            fields = list(set([p.replace("#", "/").split("/")[-1] for p, _ in self.path[bn]] + defaults)) + ["alt"]
            
            if any(re.match(".*\\_\\d+$", f) for f in fields):
                cont = container.Container(self.crawler.g, bn)

                loc_path = [(f"x{i}", x) for i, x in enumerate(cont.items())]
                fields = list(zip(*loc_path))[0]

                def _Entry(*args):
                    return list(args)
            else:
                loc_path = self.path[bn]

                # pyrefly: ignore [bad-class-definition] # self.name is already sanitised before cosntruction
                _Entry = collections.namedtuple(f"{self.name}_{counter}", fields)
            
            args = [None] * len(fields)
            field_to_idx = {f: i for i, f in enumerate(fields)}
            for i, (p, o) in enumerate(loc_path):
                kw = p.replace("#", "/").split("/")[-1]
                args[field_to_idx[kw]] = self.contract_branch(o, defaults, counter + i + 1)
                    
            return _Entry(*args)

    def __init__(self, g, where_objof_isa_ = None, category_name = "", attributes = []):
        """
        - Parameters:
            - g: the RDF graph
            - where_objof_isa_: list of the form [predicate, [list of admissible objects]]
            - category_name: the name (i.e., type) of entity that the DFS traversal is meant to summarise
            - attributes: a list of additional attributes that have to be retrieved alongside those specified by where_objof_isa_
        """
        self.g = g

        self.attributes = attributes

        # Prepare filter
        if where_objof_isa_ is None or len(where_objof_isa_[1]) == 0:
            self.filter = [None, lambda x, y: True]
            self.fields = []
        else:
            rdf_type = terminology.rdf["type"]
            def type_is_admissible(node, g):
                obj_type = list(g.objects(node, rdf_type))
                return len(obj_type) > 0 and obj_type[0] in where_objof_isa_[1]

            self.filter = [where_objof_isa_[0], type_is_admissible]
            self.fields = where_objof_isa_[1]

        # Prepare Category namedtuple
        data_names = [re.sub(r"\W", "/", d).split("/")[-1] for d in self.fields]
        loc_key = abs(hash("".join(self.fields + ["hash"])))

        self.Category = collections.namedtuple(f"_{category_name}{loc_key}", data_names + attributes)
    
    def dfs_traversal(self, start):
        """
        Traverse the graph from start
        """
        path = {}
        filtered_bns = []

        def walk_via_bn(node, h):
            if node in filtered_bns:

                if not self.filter[1](node, h):
                    filtered_bns.remove(node)
                    return []

            for _, p,o in h.triples((node, None, None)):
                if isinstance(node, rdflib.term.BNode) or isinstance(o, rdflib.term.BNode):
                    if p == self.filter[0]:
                        filtered_bns.append(o)

                    path.setdefault(node, [])
                    path[node] += [(p, o)]
                    
                    yield o
        
        return self._BNTraversal(self, list(self.g.transitiveClosure(walk_via_bn, start)), path, filtered_bns, start.split("/")[-1].replace("-", "_"))

class TmqmRDFABoxSubgraph(factory.AbstractTmqmRDFABoxSubgraph):
    """
    A base class representing a subgraph of tmQM-RDF's ABox.

    The class has the following attributes:

    - :attr:`kgraph`: The `rdflib.Graph`_ representation of the ABox.
    - :attr:`tmqmrdf`: The parent :class:`tmqmrdfdata.TmqmRDF` instance.
    - :attr:`code`: The identifying code (CSD, tmQMg-L, chemical symbol) of the object of interest.
    - :attr:`public_code`: Alias for :attr:`code`.

    .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
    """

    name = None #: The code-level name of the type of knowledge graph represented by this class. Used by :class:`tmqmrdfdata.TmqmRDF` to determine how the graph can be accessed, as explained in :class:`tmqmrdfdata.factory.AbstractTmqmRDFABoxSubgraph`.

    def __init__(self, tmqmrdf, category, code):
        """
        :param tmqmrdf: The parent :class:`tmqmrdfdata.TmqmRDF` instance.
        :param category: One of "TMCs", "ligands", "centres", "elements".
        :param code: The identifying code (CSD, tmQMg-L, chemical symbol) of the object of interest.
        """
        super().__init__(tmqmrdf, code)
        self._rdf_file = Path(os.path.join(tmqmrdf.path, "assertions", category, f"{code}.{tmqmrdf._backend}")).absolute()
        self._kgraph = tmqmrdf._read_kgraph(self._rdf_file)

    @property
    def kgraph(self):
        """
        The `rdflib.Graph`_ representation of the ABox.

        .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
        """
        return self._kgraph

    def query(self, query_object):
        """
        Wrapper for ``self.kgraph.query()``. See `rdflib.Graph.query`_.

        .. _rdflib.Graph.query: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/#rdflib.graph.Graph.query
        """
        return self.kgraph.query(query_object)

    def _get_property_crawler(self, data, category_name = "Resource", attributes = []):
        if data is None:
            data = []

        if type(data) not in [list, tuple]:
            data = [data]
        
        ms_hasProperty = terminology.ms["hasProperty"]
        
        return _BNCrawler(
                self.kgraph, 
                where_objof_isa_ = [ms_hasProperty, data], 
                category_name = category_name, 
                attributes = attributes
            )

class TMC(TmqmRDFABoxSubgraph):
    """
    A class representing the subgraph of tmQM-RDF describing a given TMC instance

    The class has the following attributes, in addition to those it inherits:
        
    - :attr:`tmc_name`: Alias for :attr:`code`.
    - :attr:`CSD_code`: Alias for :attr:`code`.
    """

    name = "TMC"
    
    def __init__(self, tmqmrdf, tmc_name):
        """
        :param tmqmrdf: The parent :class:`tmqmrdfdata.TmqmRDF` instance.
        :param tmc_name: The CSD code of the TMC.
        """
        super().__init__(tmqmrdf, "TMCs", tmc_name)

        self.tmc_name = tmc_name
        """Alias for :attr:`code`"""
        self.CSD_code = tmc_name
        """Alias for :attr:`code`"""
        
        self._raw_atoms = list(self.kgraph.subject_objects(
                            terminology.tmA["isAtom"]
                        ))
        self._raw_atbonds = self._get_raw_atbonds()
        self._raw_ligs, self._raw_mc = self._get_raw_ligand_components()
        self._raw_lbonds = self._get_raw_lbonds()
        self._raw_tmc = next(self.kgraph.subjects(terminology.cmT["hasMetalCentre"]))

    def atoms(self, data = None, alt = "tmQM"):
        """
        Retrieve the list of atoms in the molecular graph of the TMC.

        :param data: Either None, an `rdflib.term.URIRef`_, or a list of such objects. If different from None, the given URIs indicate 
            which properties should be retrieved alongside with the list of atoms. URIs must belong to the ``tmAp`` prefix. Default: None.
        :param alt: One of "tmQM" or "tmQMg". In case a requested property is specified in both of these datasets, the one coming from the "alt" dataset will be absorbed into an ``alt`` attribute of the 
               `collections.namedtuple`_ representing the property.
        

        :returns: A dictionary where keys are `rdflib.term.URIRef`_ representing atoms and values are `collections.namedtuple`_ objects with the following attributes:
                
                  - `symbol`: The `rdflib.term.URIRef`_ of the chemical symbol of the atom;
                  - if properties are requested (via the ``data`` parameter), an attribute corresponding to the suffix of each requested property. The value of the attribure is a `collections.namedtuple`_ mirroring the set of directed paths starting at the URI of the property object in the RDF graph.
                    As a rule of thumb, predicates are turned into attributes of the tuple(s), objects are turned into Python objects if they are URIs/literals, and turned into a nested named tuple if they are blank nodes.
                    Instances of `rdfs:Container`_ are an exception, as they are turned in lists where objects are converted again using the same mechanism above. Please refer to the `tmQM-RDF documentation`_.
        
        .. _rdflib.term.URIRef: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef
        .. _collections.namedtuple: https://docs.python.org/3/library/collections.html#collections.namedtuple
        .. _rdfs:Container: https://www.w3.org/TR/rdf-schema/#ch_containervocab
        .. _tmQM-RDF documentation: https://github.com/luca-cibinel/tmQM-RDF

        """
        bn_crawler = self._get_property_crawler(data, "AtomInstance", ["symbol"])

        atoms = {
            atom: bn_crawler.dfs_traversal(atom).contract(
                    defaults = ["optimisation", "singlepoint"],
                    alt = alt,
                    symbol = el
                )
            for atom, el in self._raw_atoms
        }
        
        return atoms    
    
    def bonds(self, data = None, alt = "tmQM"):
        """
        Retrieve the list of atomic bonds in the molecular graph of the TMC.

        :param data: Either None, an `rdflib.term.URIRef`_, or a list of such objects. If different from None, the given URIs indicate 
            which properties should be retrieved alongside with the list of atom bonds. URIs must belong to the ``tmBp`` prefix. Default: None.
        :param alt: One of "tmQM" or "tmQMg". In case a requested property is specified in both of these datasets, the one coming from the "alt" dataset will be absorbed into an ``alt`` attribute of the 
               `collections.namedtuple`_ representing the property.
        

        :returns: A dictionary where keys are `rdflib.term.URIRef`_ representing bonds and values are `collections.namedtuple`_ objects with the following attributes:
                
                  - `atoms`: The list of the two `rdflib.term.URIRef`_ representations of the atoms in the bond;
                  - if properties are requested (via the ``data`` parameter), the same mechanism descibed in the returned value of :meth:`atoms` applies.

        .. _rdflib.term.URIRef: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef
        .. _collections.namedtuple: https://docs.python.org/3/library/collections.html#collections.namedtuple
        """
        bn_crawler = self._get_property_crawler(data, "AtomicBondInstance", ["atoms"])

        bonds = {
            bond: bn_crawler.dfs_traversal(bond).contract(
                    defaults = ["optimisation", "singlepoint"],
                    alt = alt,
                    atoms = [at1, at2]
                )
            for bond, (at1, at2) in self._raw_atbonds.items()
        }

        return bonds

    def lbonds(self):
        """
        Retrieve the list of ligand-metal centre bonds the TMC.

        :return: A dictionary where keys are `rdflib.term.URIRef`_ representing ligand-level bonds and values are `collections.namedtuple`_ objects with the following attributes:
                 
                 - `ligand`: the `rdflib.term.URIRef`_ of the ligand participating in the bond;
                 - `atoms`: the list of the `rdflib.term.URIRef`_ representations of the atoms in the ligand bond;
                 - `bonds`: the list of the `rdflib.term.URIRef` representations of the atom-metal centre bonds corresponding to the atoms in `atoms`.
        """
        _LigandBondInstance = collections.namedtuple(f"_LigandBondInstance{abs(hash('hash'))}", ["ligand", "bonds", "atoms"])

        lbonds = {
            lbond: _LigandBondInstance(
                **lbond_data
            )
            for lbond, lbond_data in self._raw_lbonds.items()
        }

        return lbonds

    def ligands(self):
        """
        Retrieve the list of ligands the TMC.

        :return: A dictionary where keys are `rdflib.term.URIRef`_ representing ligands and values are `collections.namedtuple`_ objects with the following attributes:
                 
                 - `symbol`: the `rdflib.term.URIRef`_ of the tmQMg-L code of the ligand species;
                 - `atoms`: the list of the `rdflib.term.URIRef`_ representations of the atoms in the ligand.

        """
        _LigandInstance = collections.namedtuple(f"_LigandInstance{abs(hash('hash'))}", ["symbol", "atoms"])

        ligs = {
            lig: _LigandInstance(
                **lig_data
            )
            for lig, lig_data in self._raw_ligs.items()
        }

        return ligs

    def centre(self, as_tuple = True):
        """
        Retrieve the metal centre of the TMC.

        :param as_tuple: if True, returns the result as a tuple of the form ``(metal_centre_uri, metal_centre_data)`` instead of a dictionary of the form ``{metal_centre_uri: metal_centre_data}`` (added for compatibility with the output of the other functions). Default: True.

        :return: A tuple/dictionary as described above where:
                 
                 - `metal_centre_uri`: the `rdflib.term.URIRef`_ of the metal centre;
                 - `metal_centre_data`: a `collections.namedtuple`_ with the following attributes:
                 - `symbol`: the `rdflib.term.URIRef`_ of the metal centre (as a ligand level object);
                 - `atoms`: the (singleton) list of the `rdflib.term.URIRef`_ representation of the metal centre atom.
        """
        _MetalCentreInstance = collections.namedtuple(f"_MetalCentreInstance{abs(hash('hash'))}", ["symbol", "atoms"])
        (mc, mc_data), = self._raw_mc.items()

        if as_tuple:
            return mc, _MetalCentreInstance(**mc_data)

        return {
                mc: _MetalCentreInstance(
                    **mc_data
                )
            }
    
    def complex(self, data = None, alt = "tmQM", as_tuple = True):
        """
        Retrieve the complex-level representation of the TMC.

        :param data: either None, an `rdflib.term.URIRef`_, or a list of such. If different from None, the given URIs indicate which properties should be retrieved alongside with the TMC. URIs must belong to the `cmTp` prefix. Note: even if a property is marked in tmQM-RDF as a "meta data", it is treated as any other property by this function. Default: None.
        :param alt: one of "tmQM" or "tmQMg". In case a requested property is specified in both of these datasets, the one coming from the `alt` dataset will be absorbed into an `alt` attribute of the `collections.namedtuple`_ representing the property.
        :param as_tuple: if True, returns the result as a tuple of the form ``(complex_uri, complex_data)`` instead of a dictionary of the form ``{complex_uri: complex_data}`` (added for compatibility with the output of the other functions).

        :return: A tuple/dictionary as described above where:
                 
                 - `complex_uri`: the `rdflib.term.URIRef`_ of the complex-level representation of the TMC;
                 - `complex_data`: a `collections.namedtuple` with the following attributes:
                    
                    - if properties are requested (via the ``data`` parameter), the same mechanism descibed in the returned value of :meth:`atoms` applies.
        """
        bn_crawler = self._get_property_crawler(data, "TransitionMetalComplexInstance")

        tmcdata = bn_crawler.dfs_traversal(self._raw_tmc).contract(
                        defaults = ["optimisation", "singlepoint"],
                        alt = alt
                    )

        if as_tuple:
            return self._raw_tmc, tmcdata

        return {
                self._raw_tmc: tmcdata
            }

    def _get_raw_atbonds(self):
        
        half_bonds = self.kgraph.subject_objects(terminology.tmS["b"], unique = True)

        bonds = {}

        for at, bnd in half_bonds:
            bonds[bnd] = bonds.get(bnd, []) + [at]

        return bonds
    
    def _get_raw_ligand_components(self):
        
        lig_symbols = self.kgraph.subject_objects(terminology.lgL["isLigand"], unique = True)

        ligs = {
            lig: {
                "symbol": symbol,
                "atoms": list(self.kgraph.objects(lig, terminology.lgL["hasAtom"], unique = True))
            } for lig, symbol in lig_symbols
        }

        cnt_symbol = list(self.kgraph.subject_objects(terminology.lgC["isMetalCentre"]))[0]
        
        centre = {
            cnt_symbol[0]: {
                "symbol": cnt_symbol[1],
                "atoms": list(self.kgraph.objects(cnt_symbol[0], terminology.lgC["hasAtom"]))
            }
        }

        return ligs, centre
    
    def _get_raw_lbonds(self):
        mc = next(iter(self._raw_mc.values()))["atoms"][0]
        half_lbonds = self.kgraph.subject_objects(terminology.lgS["bLl"], unique = True)
        
        bonds = dict()
        for lig, lbnd in half_lbonds:
            bonds.setdefault(lbnd, {})
            bonds[lbnd]["ligand"] = lig
            bonds[lbnd].setdefault("bonds", [])
            bonds[lbnd].setdefault("atoms", [])

            for a in self.kgraph.objects(lbnd, terminology.lgB["hasBindingAtom"]):
                bonds[lbnd]["bonds"] += [b for b, ats in self._raw_atbonds.items() if (mc in ats) and (a in ats)]
                bonds[lbnd]["atoms"] += [a]

        return bonds
    
    def skeleton(self):
        """
        Computes the "skeleton" of a TMC (i.e. the RDF graph obtained from the corresponding tmQM-RDF entry via a depth-first search, rooted at the TMC node, allowed to move only via URIs) as an auxiliary RDF graph.

        :return: The `rdflib.Graph`_ representing the skeleton.

        .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
        """
        
        # Extract TMC node
        source = self._raw_tmc
        
        # Perform DFS
        skel = rdflib.Graph()
        
        to_parse = [source]
        visit = []
        
        while len(to_parse) > 0:
            subj = to_parse.pop()
            visit += [subj]
            
            for s, p, o in self.kgraph.triples((subj, None, None)):
                if isinstance(o, rdflib.URIRef):
                    skel.add((s, p, o))
                    
                    if o not in visit:
                        to_parse += [o]
                        
        return skel

    def as_graphviz(self, layout = "neato"):
        """
        Converts the RDF subgraph into a `graphviz`_ graphical representation.

        :param layout: The desired graphviz layout, one of "dot" or "neato". Default: "neato".

        :return: A `graphviz.Source`_ object.

        .. _graphviz: https://graphviz.readthedocs.io/en/stable/manual.html
        .. _graphviz.Source: https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Source
        """
        
        # Prepare individual node/edge attributes decalarations
        node_statements = {
            at.split("/")[-1]: dict() for at, _ in self._raw_atoms
        }

        edge_statements = {
            (at1.split("/")[-1], at2.split("/")[-1]): dict() for at1, at2 in self._raw_atbonds.values()
        }

        # Identify special attributes (related to bonds with the metal centre)
        centre_class, centre_name = next(iter(self._raw_mc.values())).values()
        centre_class = centre_class.split("/")[-1]
        centre_name = centre_name[0].split("/")[-1]
        centre_cluster_name = "cluster_metal_centre_" + centre_class # Will be needed also later

        centre_lig_bonds = []
        centre_bonded_atoms = []
        
        # For each bond, isolate those that involve the metal centre
        #   Also, identify if the metal centre is the first (tail) or the second (head)
        #   element of the bond and specify ltail/lhead accordingly
        for edge in self._raw_atbonds.values():
            edge = (edge[0].split("/")[-1], edge[1].split("/")[-1])
            if centre_name in edge:
                centre_lig_bonds += [edge]
                centre_bonded_atoms += [edge[1] if edge[0] == centre_name else edge[0]]

                tail_key = "ltail" if edge[0] == centre_name else "lhead"
                edge_statements[edge] = {
                    tail_key: centre_cluster_name,
                    "len": "3",
                    "style": "dashed"
                }

        for at in centre_bonded_atoms:
            node_statements[at] = {
                "peripheries": "2"
            }

        # Define the graph object
        #
        # Create a graph and initialize the graph-level aesthetic properties (font and rankdir)
        #
        # Then add the graph-level attributes for nodes and edges
        G = graphviz.Graph(
            name = self.CSD_code,
            graph_attr = {
                "fontname": "Helvetica,Arial,sans-serif",
                "rankdir": "LR",
                "compound": "true",
                "layout": layout
            },
            node_attr = {
                "fontname": "Helvetica,Arial,sans-serif",
                "penwidth": "1.0",
                "color": "black"
            },
            edge_attr = {
                "fontname": "Helvetica,Arial,sans-serif",
                "len": "0.6"
            }
        )
        
        # Create elemental subgraphs
        #
        # For each element encountered in the TMC, create a subgraph which collects all the atoms which possess
        # that element, and then for each subgraph define the attributes that apply a unique style to every atom
        # of the given element
        
        # Extract the set of the elements found in the TMC
        elements = set([el.symbol.split("/")[-1] for el in self.atoms().values()])
        
        # Then, for each element...
        for el in elements:
            # Extract the PubChem information relative to the given element
            el_col = _PubChemCPKColors[el]
            
            # Set up a font color: white for carbon (because of the dark background), black for all the others
            font_col = "black"
            if el == "C":
                font_col = "white"
            
            # Define the node attributes for all the nodes in the subgraph
            node_size = "0.3" if el == "H" else "0.5"
            fontsize = "7" if el == "H" else "14"

            subg_node_attr = {
                "style": "filled",
                "fillcolor": f"#{el_col}",
                "label": el,
                "fontcolor": font_col,
                "width": node_size,
                "height": node_size,
                "fontsize": fontsize,
                "fixedsize": "true"
            }

            # Create subgraph
            with G.subgraph(name = f"subgraph_{el}", node_attr = subg_node_attr) as sg:
                for el_occurrence in [el_occurrence for el_occurrence, el0 in self.atoms().items() if el0.symbol.split("/")[-1] == el]:
                    sg.node(el_occurrence.split("/")[-1], **node_statements[el_occurrence.split("/")[-1]])

        # Create TMC cluster (will contain ligands, metal centre, and edges to the centre)
        cluster_style = [
            f"label = \"{self.CSD_code}\";\n",
            "color = \"orange\";\n",
            "fontcolor = \"orange\";\n"
        ]
        TMC = graphviz.Graph(f"cluster_TMC_{self.CSD_code}", body = cluster_style)

        # Create metal centre cluster (structurally speaking, same as a ligand)    
        cluster_style = [
            f"label = \"Metal centre: {centre_class}\";\n",
            "color = \"blue\";\n",
            "fontcolor = \"blue\";\n"
        ]
        node_statements[centre_name].update({"peripheries": "3"})
        with TMC.subgraph(name = centre_cluster_name, body = cluster_style) as cl:
            cl.node(centre_name, **node_statements[centre_name])
        
        # Create ligand clusters
        #
        # For each ligand, define a cluster that will encompass all the atoms and all the chenical bonds
        # that belong to the ligand. A bond is said to belong to the ligand when both its ends belong to the ligand
        
        # See self._get_ligands_components docstring for a description of ligand
        #   For each ligand...
        for ligand_name, ligand in self._raw_ligs.items():
            # Extract all the node statements associated with the ligand
            #   except for those bonded to the metal centre (those will be added separately)
            nodes_in_ligand = [at for at in ligand["atoms"] if at not in centre_bonded_atoms]
            
            # Identify the atoms bonded to the centre and put them in their own subgraph
            nodes_bound_to_centre = [at for at in ligand["atoms"] if at in centre_bonded_atoms]
            
            btc_subgraph = graphviz.Graph(
                name = "bound_to_centre",
                graph_attr = {"rank": "same"}
            )
            for at in nodes_bound_to_centre:
                btc_subgraph.node(at, **node_statements[at])
            
            # Extract all the edge statements that belong to the ligand
            edges_in_ligand = []
            
            for edge in self._raw_atbonds.values():
                if edge[0] in ligand["atoms"] and edge[1] in ligand["atoms"]:
                    edges_in_ligand += [[edge[0].split("/")[-1], edge[1].split("/")[-1]]]
            
            # Create the cluster using the nodes and the edges and label it according
            #   to the ligand id
            cluster_style = [
                f"label = \"{ligand['symbol'].split('/')[-1]}\";\n",
                "color = \"blue\";\n",
                "fontcolor = \"blue\";\n"
            ]
            with TMC.subgraph(name = f"cluster_{ligand_name.split("/")[-1].replace("-", "__")}", body = cluster_style) as cl:
                for at in nodes_in_ligand:
                    at = at.split("/")[-1]
                    cl.node(at)
                for edge in edges_in_ligand:
                    edge = [edge[0].split("/")[-1], edge[1].split("/")[-1]]
                    cl.edge(*edge)

                cl.subgraph(btc_subgraph)
        
        # Add metal centre-binding atoms edges:
        for edge in centre_lig_bonds:
            TMC.edge(*edge, **edge_statements[edge])

        # Add TMC cluster to the graph object
        
        G.subgraph(TMC)
        
        return G
    
    def view(self, format = "png", filename = None, layout = "neato"):
        """
        Produces an image of the TMC rendered via the `graphviz`_ module and visualises it.
        
        :param format: the desired output format for the resulting graphviz object (pdf, png, svg, ...).
        :param filename: the name of the file (without the extension) to which the output should be saved (optional).
        :param layout: the desired layout engine, one of '"dot" and "neato". Default: "neato".
        """
        src = self.as_graphviz(layout)
        src.format = format
        
        if filename is None:
            src.view(tempfile.mktemp(".gv"), cleanup = True)
        else:
            src.view(filename, cleanup = True)
            
    def render(self, format = "png", filename = None, layout = "neato"):
        """
        Saves an image of the TMC rendered via the `graphviz`_ module, without visualising it.
        
        :param format: the desired output format for the resulting graphviz object (pdf, png, svg, ...).
        :param filename: the name of the file (without the extension) to which the output should be saved.
        :param layout: the desired layout engine, one of '"dot" and "neato". Default: "neato".
        """
        src = self.as_graphviz(layout)
        src.format = format
        
        if filename is None:
            raise RuntimeError("'filename' cannot be None when rendering without viewing! To only visualise the knowledge graph, use .view() .")
        else:
            src.render(filename, cleanup = True)

class Ligand(TmqmRDFABoxSubgraph):
    """
    A class representing the subgraph of tmQM-RDF describing a given ligand species

    The class has the following attributes, in addition to those it inherits:
    
    - :attr:`tmqmgl_code`: Alias for :attr:`code`.
    """
    name = "ligand"
    
    def __init__(self, tmqmrdf, tmqmgl_code):
        """
        :param tmqmrdf: -the parent :class:`tmqmrdfdata.TmqmRDF` instance.
        :param tmqmgl_code: Alias for :attr:`code`.
        """
        super().__init__(tmqmrdf, "ligands", tmqmgl_code)

        self.tmqmgl_code = tmqmgl_code
        """Alias for :attr:`code`."""

        self._raw_ligand = next(self.kgraph.subjects(terminology.rdf["type"], terminology.lgLr["LigandClass"]))

    def species(self, data = None, alt = None, as_tuple = True):
        """
        Retrieve the RDF representation of the ligand species.

        :param data: either None, an `rdflib.term.URIRef`_, or a list of such. If different from None, the given URIs indicate which properties should be retrieved. URIs must belong to the `lgLrp` prefix. Default: None.
        :param alt: ignored. Added for compatibility with the other functions.
        :param as_tuple: if True, returns the result as a tuple of the form ``(species_uri, species_data)`` instead of a dictionary of the form ``{species_uri: species_data}`` (added for compatibility with the output of the other functions). Default: True.

        :return: A tuple/dictionary as described above where:
                 
                 - `species_uri`: the `rdflib.term.URIRef`_ of the RDF representation of the species;
                 - `species_data`: a `collections.namedtuple`_ with the following attributes:
                    
                    - if properties are requested (via the `data` parameter), an attribute corresponding to the suffix of each requested property. The value of the attribure is a `collections.namedtuple`_ mirroring the set of directed paths starting at the URI of the property object in the RDF graph. As a rule of thumb, predicates are turned into attributes of the tuple(s), objects are turned into Python objects if they are URIs/literals, and turned into a nested named tuple if they are blank nodes. Instances of `rdfs:Container`_ are an exception, as they are turned in lists where objects are converted again using the same mechanism above. Please refer to the `tmQM-RDF documentation`_.
        """
        bn_crawler = self._get_property_crawler(data, "LigandSpecies")

        ligdata = bn_crawler.dfs_traversal(self._raw_ligand).contract(
                        defaults = ["optimisation", "singlepoint", "basedOn"],
                        alt = alt
                    )

        if as_tuple:
            return self._raw_ligand, ligdata

        return {
                self._raw_ligand: ligdata
            }

class Centre(TmqmRDFABoxSubgraph):
    """
    A class representing the subgraph of tmQM-RDF describing a given metal centre species.

    The class has the following attributes, in addition to those it inherits:

    - :attr:`symbol`: Alias for :attr:`code`.
    """
    name = "centre"
    
    def __init__(self, tmqmrdf, symbol):
        """
        :param symbol: The chemical symbol of the metal centre.  
        """
        super().__init__(tmqmrdf, "centres", "MetalCentre_" + symbol)

        self.symbol = symbol
        """Alias for :attr:`code`."""

        self.public_code = symbol

class Element(TmqmRDFABoxSubgraph):
    """
    A class representing the subgraph of tmQM-RDF describing a given element.

    The class has the following attributes, in addition to those it inherits:

    - :attr:`symbol`: Alias for :attr:`code`.
    """
    name = "element"
    
    def __init__(self, tmqmrdf, symbol):
        """
        - **Parameters**:
            - `symbol`: the chemical symbol of the element.
        """
        super().__init__(tmqmrdf, "elements", symbol)

        self.symbol = symbol
        """Alias for :attr:`code`"""