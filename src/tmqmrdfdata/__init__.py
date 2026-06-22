"""
tmqmrdfdata is an rdflib-based Python package designed to support and facilitate the interaction with 

tmQM-RDF: a Knowledge Graph Representing Transition Metal Complexes.

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

from . import terminology
from . import assertions

from tqdm import tqdm

import multiprocessing
import urllib.request
import collections
import rdflib_hdt
import tempfile
import zipfile
import rdflib
import json
import os

__all__ = [
    "download_tmQM_RDF_knowledge_graph",
    "TmqmRDF",
    "terminology",
    "assertions"
]

def download_tmQM_RDF_knowledge_graph(dir = ".", version = "latest", hdt_format = False):
    """
    Downloads the tmQM-RDF knowledge graph from its [GitHub repository](https://github.com/luca-cibinel/tmQM-RDF-archive) using the GitHub REST API.

    - **Parameters**:
        - `dir`: the directory where the data should be saved. Default: '.'.
        - `version`: the desired tmQM-RDF version, can be either 'latest' or any other available version number (without leading 'v') as a string. Default: 'latest'.
        - `hdt_format`: download the HDT-equivalent version of the knowledge graph instead of the standard .ttl encoded once. Default: False 
    """
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

    if hdt_format:
        assets = release["assets"]

        assert len(assets) == 1 and assets[0]["name"].startswith("hdt"), \
            f"Unable to identify HDT asset (version: {version}) at 'https://github.com/luca-cibinel/tmQM-RDF-archive/'."

        fetch_url = assets[0]["browser_download_url"]
    else: 
        fetch_url = release["zipball_url"]

    print("")
    print("Format requested:", ".hdt" if hdt_format else ".ttl")
    print("Release identified:")
    print("\tName:", vname)
    print("\tTag:", tag)
    print("\tURL:", html)
    print("\tDownload URL:", fetch_url)
    print("")

    print(f"Downloading from 'Download URL' to '{dir}' ...")
    temp_zipname = tempfile.mktemp(".zip", dir = dir)
    #with urllib.request.urlopen(fetch_url) as response, open(temp_zipname, "wb") as f:
    #    shutil.copyfileobj(response, f)
    chunk_size = 1024*8
    with urllib.request.urlopen(fetch_url) as response, open(temp_zipname, "wb") as f:
        total_size = int(response.headers.get("Content-Length", 0))

        with tqdm(total = total_size, unit = "B", unit_scale = True, unit_divisor = 1024, desc = "Progress") as pbar:
            while chunk := response.read(chunk_size):
                f.write(chunk)
                pbar.update(len(chunk))

    print("Extracting archive...")
    with zipfile.ZipFile(temp_zipname) as zipf:
        zipf.extractall(dir)
        root_name = zipf.infolist()[0].filename.split(os.sep)[0]

    print("Cleanup...")
    os.remove(temp_zipname)

    new_dirname = f"tmQM-RDF-{vname}"
    if hdt_format:
        new_dirname = "hdt-" + new_dirname
    if new_dirname not in os.listdir(dir):
        os.rename(os.path.join(dir, root_name), os.path.join(dir, new_dirname))
    else:
        print("\n-- Unable to rename root directory due to naming conflict --")
        print(f"-- The downloaded data can be found in {os.path.join(dir, root_name)}")
        print("")

    print("Download complete!")

class _TmqmRDF_HDTStore(rdflib_hdt.HDTStore):
    """
    An internal utility class that extends rdflib_hdt.HDTStore to include the default namespaces
    defined by tmqmrdfdata.terminology. This allows the correct identification of the namespaces
    defined in tmQM-RDF when using the 'rdflib_hdt' backend.

    The namespace logic has been derived from that of rdflib.plugins.stores.memory.Memory.

    See rdflib_hdt.HDTStore and rdflib.plugins.stores.memory.
    """

    def __init__(self, path, mapped = True, indexed = True, safe_mode = True, configuration = None, identifier = None):
        super(_TmqmRDF_HDTStore, self).__init__(path, mapped, indexed, safe_mode, configuration, identifier)

        self.__prefix = terminology.DEFAULT_PREFIXES
        self.__namespace = terminology.DEFAULT_NAMESPACES

    def namespace(self, prefix: str):
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        for prefix, namespace in self.__namespace.items():
            yield prefix, namespace

class TmqmRDF(collections.UserDict):
    """
    A user-friendly interface to the tmQM-RDF knowledge graph.

    This class is a dictionary-like object that internally stores selected subgraphs of tmQM-RDF.
    Namely, a subgraph can be accessed via the key (\<category\>, \<code\>), where:
    - category can be either "TMC", "ligand", "centre" or "element";
    - code is the corresponding code of the desired object (either the CSD code, the tmQMg-L ligand id, or the chemical symbol for both centres and elements).  
    
    Due to the size of tmQM-RDF, not all subgraphs are immediately loaded upon class instantiation. The desired subgraphs have to be fetched using the `.fetch` method. For quick access
    to single TMCs, ligand species or elements, the methods `.tmc`, `.ligand`, `.centre`, or `.element` can also be used.

    Each subgraph (the value returned by `self[<category>, <code>])` is an instance of tmqmrdfdata.assertions.TmqmRDFABoxSubgraph, and exposes its rdf triples via the `.kgraph` attribute, which is
    an [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) object. Each category has unique attributes and dedicated methods to quickly retrieve properties and/or visualise the corresponding chemical object. See the related documentation.

    - **Attributes**:
        - `path`: the path to the root of the tmQM-RDF directory.
        - `index`: a dictionary with keys 'centres', 'elements', 'ligands', and 'TMCs' whse values are the lists of the available entries 
            for the corresponding assertions.
        - `tbox`: an instance of `tmqmrdfdata.terminology.TmqmRDFTBoxSubgraph` representing the TBox.
        - `t`: alias for `tbox`.
    """

    def __init__(self, path):
        """
        Initialises the interface.

        - **Parameters**:
            - `path`: the path to the root dir of tmQM-RDF, i.e., the `<root>` node in the tree
        ```bash
        <root>
        ├── assertions
        │   └── ...
        └── terminology
            └──  ...
        ```
        """
        super().__init__()

        self.path = path

        self._raw_index = {
            key: [_tvar for f in os.listdir(os.path.join(self.path, "assertions", key)) if not f.startswith(".") and len(_tvar := f.split(".")) == 2]
            for key in ["centres", "elements", "ligands", "TMCs"]
        }

        self.index = {
            key: [f[0] for f in value]
            for key, value in self._raw_index.items() 
        }

        extension_type = set(sum([[f[1] for f in val] for val in self._raw_index.values()], []))
        assert len(extension_type) == 1, f"Unable to identify dataset format. Found: {extension_type}; expected EXACTLY one of {list(rdflib.util.SUFFIX_FORMAT_MAP) + ["hdt"]}."

        self._backend = next(iter(extension_type))

        self.tbox = terminology.TmqmRDFTBoxSubgraph(self)
        self.t = self.tbox
    
    def _read_kgraph(self, rdf_file):
        """
        Reads a knowledge graph in the form of an rdflib.Graph object using the appropriate backend
        (either rdflib or rdflib_hdt).

        - Parameters:
            - `rdf_file`: the (full) path to the rdf file

        - Returns:
            - an rdflib.Graph instance
        """
        extension = self._backend
        if extension in rdflib.util.SUFFIX_FORMAT_MAP:
            kgraph = rdflib.Graph()
            kgraph.parse(rdf_file)
        elif extension == "hdt":
            kgraph = rdflib.Graph(store = _TmqmRDF_HDTStore(str(rdf_file)))
        else:
            raise RuntimeError(f"Specified file format (.{extension}) not recognised!")

        return kgraph

    def _read(self, args):
        """
        Instantiates an ABox subgraph.

        - Parameters:
            - args: a tuple of the form (object_code, object_class)

        - Return:
            - the instantiated class
        """
        return args[1](self, args[0])

    def fetch(self, tmcs = [], ligands = [], centres = [], elements = [], auto_fetch_tmc_components = False, n_cores = 1):
        """
        Fetches the requested subgraphs from tmQM-RDF and makes them available for access via dictionary-like syntax.

        - **Parameters**:
            - `tmcs`: the list of CSD codes of the desired TMCs.
            - `ligands`: the list of the tmQMg-L codes of the desired ligands.
            - `centres`: the list of chemical symbols of the desired metal centres.
            - `elements`: the list of chemical symbols of the desired elements.
            - `auto_fetch_tmc_components`: should the components of all requested TMCs (ligands, metal centres, elements) be automatically fetched? Default: False.
            - `n_cores`: number of cores to use for import. Default: 1.
        """

        categories = [assertions.TMC, assertions.Ligand, assertions.Centre, assertions.Element]

        for objects, Category in zip([tmcs, ligands, centres, elements], categories):
            criterion = None
            if callable(objects):
                criterion = objects
                objects = self.index[Category.name + "s"]

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
                    if criterion is not None and not criterion(obj):
                        continue

                    super().__setitem__((Category.name, obj.public_code), obj)

                    if auto_fetch_tmc_components and Category.name == "TMC":
                        local_ligands = [
                            lig_info["symbol"].split("_")[-1] for lig_info in obj._raw_ligs.values()
                            if lig_info["symbol"].split("_")[-1] not in ligands
                        ]
                        ligands += list(set(local_ligands))

                        local_centre = [
                            mc_info["symbol"].split("_")[-1] for mc_info in obj._raw_mc.values()
                            if mc_info["symbol"].split("_")[-1] not in centres
                        ]
                        centres += local_centre

                        local_elements = [
                            atom_info[1].split("/")[-1] for atom_info in obj._raw_atoms
                            if atom_info[1].split("/")[-1] not in elements
                        ]
                        elements += list(set(local_elements))

    def tmc(self, csd_code, with_components = False):
        """
        Wrapper for:
        - (equivalent code)
        ```python
        self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components)
    
        return self["TMC", csd_code]
        ```
        """
        self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components)

        return self["TMC", csd_code]

    def ligand(self, tmqmgl_code):
        """
        Wrapper for:
        - (equivalent code)
        ```python
        self.fetch(ligands = [tmqmgl_code])

        return self["ligand", tmqmgl_code]
        ```
        """
        self.fetch(ligands = [tmqmgl_code])

        return self["ligand", tmqmgl_code]

    def centre(self, symbol):
        """
        Wrapper for:
        - (equivalent code)
        ```python
        self.fetch(centres = [symbol])
    
        return self["centre", symbol]
        ```
        """
        self.fetch(centres = [symbol])

        return self["centre", symbol]

    def element(self, symbol):
        """
        Wrapper for:
        - (equivalent code)
        ```python
        self.fetch(elements = [symbol])
    
        return self["element", symbol]
        ```
        """
        self.fetch(elements = [symbol])

        return self["element", symbol]

    def as_knowledge_graph(self):
        """
        Returns a single [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) RDF graph given by the union of all the exposed subgraphs
        """

        return sum([g.rdf for g in self.values()], rdflib.Graph())
