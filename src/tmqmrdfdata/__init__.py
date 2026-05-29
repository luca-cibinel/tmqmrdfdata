#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script defines a class that converts the RDF representation of TMCs employed in tmQM-RDF
into an networkx-encoded version of one of the three representations defined below (run this script for a visual representation).

For simplicity, it relies on the tmQMg dataset and it expands it using information from tmQMg-L (linked via tmQM-RDF).
"""

import terminology
import assertions

import multiprocessing
import urllib.request
import numpy as np
import collections
import tempfile
import zipfile
import rdflib
import shutil
import json
import os

import warnings
np.warnings = warnings

def download_tmQM_RDF_knowledge_graph(dir = ".", version = "latest"):
    find_release_url = "https://api.github.com/repos/luca-cibinel/tmQM-RDF-archive/releases" + ("/latest" if version == "latest" else "")
    
    print("Sending GET requests to GitHub using GitHub REST API to identify the correct release...")
    with urllib.request.urlopen(find_release_url) as response:
        response = response.read().decode("utf-8")
    
    response = json.loads(response) # convert to python object

    if version == "latest":
        release = response
    else:
        hit = [rel for rel in response if rel["name"] == f"v{version}"]

        assert len(hit) == 1, f"Unable to identify release 'v{version}' at 'https://github.com/luca-cibinel/tmQM-RDF-archive/'."

        release = hit[0]

    tag, vname, html = release["tag_name"], release["name"], release["html_url"]
    fetch_url = release["zipball_url"]

    print("")
    print("Release identified:")
    print("\tName:", vname)
    print("\tTag:", tag)
    print("\tURL:", html)
    print("\tZipball URL:", fetch_url)
    print("")

    print(f"Downloading from Zipball URL to '{dir}' ...")
    temp_zipname = tempfile.mktemp(".zip", dir = dir)
    with urllib.request.urlopen(fetch_url) as response, open(temp_zipname, "wb") as f:
        shutil.copyfileobj(response, f)

    print("Extracting archive...")
    with zipfile.ZipFile(temp_zipname) as zipf:
        zipf.extractall(dir)
        root_name = zipf.infolist()[0].filename.split(os.sep)[0]

    print("Cleanup...")
    os.remove(temp_zipname)

    new_dirname = f"tmQM-RDF-{vname}"
    if new_dirname not in os.listdir(dir):
        os.rename(os.path.join(dir, root_name), os.path.join(dir, new_dirname))
    else:
        print("\n-- Unable to rename root directory due to naming conflict --")
        print(f"-- The downloaded data can be found in {os.path.join(dir, root_name)}")
        print("")

    print("Download complete!")

class TmQMRDF(collections.UserDict):
    """
    A user-friendly interface to the tmQM-RDF knowledge graph.
    Table of contents:
        1. Accessing tmQM-RDF subgraphs
            1.1 Merging subgraphs
        2. Subgraph attributes
        3. Import settings

    1. Accessing tmQM-RDF subgraphs
    ---
    This class is a dictionary-like object that internally stores selected subgraphs of tmQM-RDF.
    Namely, a subgraph can be accessed via the key (<category>, <code>), where:
        - category can be either "TMC", "ligand", "centre" or "element"
        - code is the corresponding code of the desired object (either the CSD code, the tmQMg-L ligand id, or the chemical symbol for both centres and elements)
    Initially, not all subgraphs are available. The desired subgraphs have to be "exposed" using the self.expose method. For quick access
    to single TMCs, ligand species or elements, the methods self.tmc, self.ligand or self.element can also be used.

    Each subgraph (the value returned by self[<category>, <code>]) exposes its rdf triples via the .rdf attribute, which is
    an rdflib.Graph object.
    
        1.1 Merging subgraphs
        See rdflib.Graph for more details on how to merge subgraphs.
        The method self.as_knowledge_graph() can be used to merge all the exposed subgraphs into a single graph.

    2. Subgraph attributes
    ---
    Additional category-specific attributes may be available. Specifically, TMCs expose the following attributes:
        - atoms: a list of pairs (atom_name, atom_element), where
            - atom_name is the name of the object representing the atom, intended
                as the last element on the URI path (e.g. if the URI is https://www.integreat.no/research/rdf/tmqm-rdf-dataset/#/atomic/atom/XXYYZZ_El1,
                the name is XXYYZZ_El1)
            - atom_element is the chemical symbol of the element of the atom, again, extracted as the last element
                of the URI path of the element object
        - atomic_bonds: a list of pairs (atom1_name, atom2_name), where atom[n]_name is the name of the atom at the
            n-th end of the bond (n = 1,2). The atoms are ordered according to the IDs assigned in the
            tmQMg dataset, with id(atom1) < id(atom2).
        - ligands: a dictionary of the form {ligand_name: {'class': ligand_id, 'components': [...]}, ...}
            where:
                - ligand_name is the name of the ligand object (intended as the last element
                    on the URI path)
                - ligand_id is the id of the reference ligand
                - components is a list of the names of the atoms that compose this instance of the ligand
        - metal_centre: a dictionary of the form {'class': centre_element, 'components': [centre_atom]}
            where:
                - centre_element is the chemical element of the metal centre
                - centre_atom is the name of the atom representing the centre at the atomic level
        - ligand_bonds: a dictionary of the form {ligand_id: bonds, }, where ligand_id is the id of the ligand the
                bond refers to, and bonds is a list of lists (in the tmQMg-L sense) of the binding atoms.
    
    3. Import settings
    ---
    The actual import behaviour behaviour of the class is governed by the method self.set_import_setting.
    By default, the following settings are enabled:
        - path_to_chem_info = None,
        - pubchem_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV?response_type=save&response_basename=PubChemElements_all",
        - request_tmc_atoms = True, 
        - request_tmc_atomic_bonds = True,
        - request_tmc_ligands = True,
        - request_tmc_ligand_bonds = True,
        - auto_expose_tmc_ligands = False
    """

    def __init__(self, path):
        """
        Main interface to tmQM-RDF.

        - Arguments:
            - path: the path to the root directory of tmQM-RDF
        """
        super().__init__()

        self.path = path
        self.import_settings = dict()
        self.set_import_settings(
            None, 
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV?response_type=save&response_basename=PubChemElements_all",
            True, 
            True, 
            True, 
            True,
            False, 
            force = False
        )

        self.tbox = terminology.TmQMRDFTBoxSubgraph(self)
        self.t = self.tbox

    def set_import_settings(
                self,
                path_to_chem_info = None,
                pubchem_url = None,
                request_tmc_atoms = None, 
                request_tmc_atomic_bonds = None,
                request_tmc_ligands = None,
                request_tmc_ligand_bonds = None,
                auto_expose_tmc_ligands = None,
                force = False
            ):
        """
        Sets the import settings. Only settings that are not None are saved. If a setting is already set and force = False,
        the corresponding argument is always discarded.

        - Arguments:
            - path_to_chem_info: a string pointing to the .csv version of the pubchem periodic table (if not present and pubchem_url is
                available, it will be downloaded to this location)
            - pubchem_url: the url from which the .csv version of the pubchem periodic table should be downloaded
            - request_tmc_atoms: when importing a TMC, should its composing atoms be extracted in a user-friendly format?
            - request_tmc_atomic_bonds: when importing a TMC, should it atomic bonds be extracted in a user-friendly format?
            - request_tmc_ligands: when importing a TMC, should its composing ligands be extracted in a user-friendly format?
            - request_tmc_ligand_bonds: when importing a TMC, should its ligand-level bonds be extracted in a user-friendly format?
            - auto_expose_tmc_ligands: when importing a TMC via self.expose, should its composing ligands be exposed as well? If True, it
                overrides request_tmc_ligands and the import will always behave as if request_tmc_ligands = True.
            - force: should the old settings be overwritten?
        """
        for key, value in locals().items():
            if key == "force":
                continue

            if value is not None and (force or key not in self.import_settings):
                self.import_settings[key] = value

    def _read(self, args):
        return args[1](self, args[0])

    def expose(self, tmcs = [], ligands = [], centres = [], elements = [], n_cores = 1):
        """
        Extract one or more subgraphs corresponding to TMCs/ligand species/elements and makes them 
        accessible via self.__getitem__

        - Arguments:
            - tmcs: iterable containing CSD codes of TMCs to extract
            - ligands: iterable containing tmQMg-L ids of ligand species to extract
            - centres: iterable containing the chemical symbols of the metal centres to extract
            - elements: iterable containing the chemical symbols of elements to extract
            - n_cores: how many processes should be used to extract the TMCs. Default: 1
        """

        categories = [assertions.TMC, assertions.Ligand, assertions.Centre, assertions.Element]

        for objects, Category in zip([tmcs, ligands, centres, elements], categories):
            with multiprocessing.Pool(processes = n_cores) as pool:
                parsed_objects = [(obj, Category) for obj in objects if (Category.name, obj) not in self.data]

                if len(parsed_objects) == 0:
                    continue

                if n_cores > 1:
                    # pool = multiprocessing.Pool(processes = n_cores)
                    parse = pool.imap_unordered
                else:
                    parse = map

                for obj in parse(self._read, parsed_objects):
                    super().__setitem__((Category.name, obj.public_code), obj)

                    if self.import_settings["auto_expose_tmc_ligands"] and Category.name == "TMC":
                        local_ligands = [lig_info["class"] for lig_info in obj.ligands.values() if lig_info["class"] not in ligands]
                        ligands += local_ligands

    def tmc(self, csd_code):
        """
        Wrapper for
            self.expose(tmcs = [csd_code])
            
            return self[("TMC", csd_code)]
        """
        self.expose(tmcs = [csd_code])

        return self["TMC", csd_code]

    def ligand(self, tmqmgl_code):
        """
        Wrapper for
            self.expose(ligands = [tmqmgl_code])

            return self["ligand", tmqmgl_code]
        """
        self.expose(ligands = [tmqmgl_code])

        return self["ligand", tmqmgl_code]

    def centre(self, pubchem_code):
        """
        Wrapper for
            self.expose(centres = [pubchem_code])

            return self["centre", pubchem_code]
        """
        self.expose(centres = [pubchem_code])

        return self["centre", pubchem_code]

    def element(self, pubchem_code):
        """
        Wrapper for
            self.expose(tmcs = [csd_code])
            self[("element", csd_code)]
        """
        self.expose(elements = [pubchem_code])

        return self["element", pubchem_code]

    def as_knowledge_graph(self):
        """
        Returns a single rdflib.Graph RDF graph given by the union of all the exposed subgraphs
        """

        return sum([g.rdf for g in self.values()], rdflib.Graph())

# %% Main
if __name__ == "__main__":
    __spec__ = None

    import sys
    bin_path = os.path.abspath(os.path.join(sys.executable, ".."))
    if bin_path not in os.environ["PATH"].split(":"):
        print(f"[ WARNING: the path {bin_path} could not be found inside os.environ['PATH']. It will be added now. ]")
        os.environ["PATH"] = f"{bin_path}:{os.environ['PATH']}"

    ROOT_DIR = os.path.abspath(".")
    while ".prj_root" not in os.listdir(ROOT_DIR):
        ROOT_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".."))
    
    instance = TmQMRDF(os.path.join(ROOT_DIR, "data", "derivative", "tmQM-RDF", "data", "v1.1"))
    instance.set_import_settings(
        path_to_chem_info = os.path.join(ROOT_DIR, "data", "raw", "pubChem", "data"),
        auto_expose_tmc_ligands = False,
        force = True
    )

    g = instance.tmc("KCEYPT")
    lig_class = instance.ligand("ligand956-0")

    tmAp = terminology.tmAp
    tmBp = terminology.tmBp

    at = g.atoms(data = [tmAp["natural_atomic_charge"]])
    bnd = g.bonds(data = [tmBp["wiberg_bond_order"], tmBp["nbo_type"]])
    lbnd = g.lbonds()
    lig = g.ligands()
    mc, mcdata = g.centre()
    tmc, tmcdata = g.complex(data = [terminology.cmTp["element_counts"], terminology.cmTp["dipole_moment"]])

    lclass, ldata = lig_class.species(data = terminology.lgLrp["denticity_hapticity_orders"])

    g.view()