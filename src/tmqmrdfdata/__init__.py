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
from . import _pages

from tqdm.contrib import concurrent
from tqdm import contrib
from tqdm import tqdm

import urllib.request
import collections
import rdflib_hdt
import itertools
import functools
import tempfile
import zipfile
import rdflib
import json
import os

__all__ = [
    "download_tmQM_RDF_knowledge_graph",
    "concurrent_map",
    "TmqmRDF",
    "terminology",
    "assertions"
]

# %% Lookup utils ====
no = _pages._LookupEngine(None)
"""The global :doc:`Online Lookup Engine </usage/lookup>`."""

# %% Download utils ====
def _download_zip(fetch_url, dir, new_dirname = None):
    """
    Utility function to download a zip file from a given URL, unzip it, and then cleanup.

    :param fetch_url: The target URL.
    :param dir: The directory where the file should be downloaded to.
    :param new_dirname: None, or the new name that should be assigned to the root directory containing the unzipped files, if any. The function checks for name collisions.

    :return: The name of the root directory
    """

    print(f"Downloading from 'Download URL' to '{dir}' ...")
    temp_zipname = tempfile.mktemp(".zip", dir = dir)
    
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

    if new_dirname is not None:

        if new_dirname not in os.listdir(dir):
            os.rename(os.path.join(dir, root_name), os.path.join(dir, new_dirname))
        else:
            print("\n-- Unable to rename root directory due to naming conflict --")
            print(f"-- The downloaded data can be found in {os.path.join(dir, root_name)}")
            print()

            new_dirname = root_name

    return new_dirname

def _download_hdt_indices(index_urls, dataset_root_dir):
    print("Downloading HDT index files...")
    
    for fname, url in index_urls:
        print(f"\nCurrent Download URL: {url}")

        # index naming convention:
        #     hdt-index-tmQM-RDF-v[version]__[path to folder separated by '_']_._[notes].zip
        target_path = fname.replace(".zip", "").split("__")[1].split("_._")[0]
        target_path = target_path.split("_")
        target_path = os.path.join(dataset_root_dir, *target_path)

        _download_zip(url, target_path, None)

    print()
    print("Validating HDT index files...")

    walk = list(os.walk(dataset_root_dir))
    for dir, _, files in tqdm(walk):
        for f in tqdm(files, leave = False):
            if f.endswith(".hdt"):
                assert f + ".index.v1-1" in files, f"Error! In dir {dir}, file {f} has no index!"

def download_tmQM_RDF_knowledge_graph(dir = ".", version = "latest", hdt_format = False, hdt_index = True):
    """
    Downloads the tmQM-RDF knowledge graph from its `GitHub repository`_ using the `GitHub REST API`_.
    The flag _hdt\_format_ allows to download the `HDT`_ version of the dataset instead of the regular Turtle encoded one
    (recommended for faster performance).

    .. _GitHub repository: https://github.com/luca-cibinel/tmQM-RDF-archive

    .. _GitHub REST API: https://docs.github.com/en/rest?apiVersion=2026-03-10

    .. _HDT: https://www.rdfhdt.org/what-is-hdt/

    :param dir: The directory where the data should be saved. Default: '.'.
    :param version: The desired tmQM-RDF version, can be either 'latest' or any other available version number (without leading 'v') as a string. Default: 'latest'.
    :param hdt_format: Download the HDT-equivalent version of the knowledge graph instead of the standard .ttl encoded once. Default: False.
    :param hdt_index: If True, download the precomputed HDT index files (if HDT has been requested). Default: True.
    """
    find_release_url = "https://api.github.com/repos/luca-cibinel/tmQM-RDF-archive/releases" + ("/latest" if version == "latest" else "")
    
    print("Sending GET request to GitHub using GitHub REST API to identify the correct release...")
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

    fetch_url = None
    index_urls = []
    if hdt_format:
        assets = release["assets"]

        for asset in assets:
            if asset["name"].startswith("hdt-index"):
                index_urls += [(asset["name"], asset["browser_download_url"])]
            elif asset["name"].startswith("hdt"):
                fetch_url = asset["browser_download_url"]
    else: 
        fetch_url = release["zipball_url"]

    assert fetch_url is not None, f"Unable to locate download link for release {vname}"

    print()
    print("Format requested:", ".hdt" if hdt_format else ".ttl")
    print("Release identified:")
    print("\tName:", vname)
    print("\tTag:", tag)
    print("\tURL:", html)
    print("\tDownload URL:", fetch_url)
    print()

    # Download dataset
    new_dirname = f"tmQM-RDF-{vname}"
    if hdt_format:
        new_dirname = "hdt-" + new_dirname

    dataset_root_dir = _download_zip(fetch_url, dir, new_dirname)

    # Download HDT indices
    if hdt_format and hdt_index:
        _download_hdt_indices(index_urls, os.path.join(dir, dataset_root_dir))

    # Write link to github repository (for single file visualisation)
    with open(os.path.join(dir, dataset_root_dir, ".pages"), "w") as f:
        f.write(str({
                "base_link": f"https://github.com/luca-cibinel/tmQM-RDF-archive/blob/{vname}/",
                "version": vname
            })
        )

    print("Download complete!")

# %% Dataset utils ====

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
        yield from self.__namespace.items()

class TmqmRDF(collections.UserDict):
    """
    A user-friendly interface to the tmQM-RDF knowledge graph.

    This class is a dictionary-like object that internally stores selected subgraphs of tmQM-RDF.
    Namely, a subgraph can be accessed via the key (\<category\>, \<code\>), where:

    - category can be either "TMC", "ligand", "centre" or "element";
    - code is the corresponding code of the desired object (either the CSD code, the tmQMg-L ligand id, or the chemical symbol for both centres and elements).  
    
    Due to the size of tmQM-RDF, not all subgraphs are immediately loaded upon class instantiation. The desired subgraphs have to be fetched using the :meth:`fetch` method. For quick access
    to single TMCs, ligand species or elements, the methods :meth:`tmc`, :meth:`ligand`, :meth:`centre`, or :meth:`element` can also be used.

    Each subgraph (the value returned by `self[<category>, <code>]`) is an instance of :class:`assertions.TmqmRDFABoxSubgraph`, and exposes its rdf triples via the :attr:`assertions.TmqmRDFABoxSubgraph.kgraph` attribute, which is
    an `rdflib.Graph`_ object. Each category has unique attributes and dedicated methods to quickly retrieve properties and/or visualise the corresponding chemical object. See the related documentation.

    .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/

    The class has the following attributes:

    - :attr:`no` The local :doc:`Online Lookup Engine </usage/lookup>`.
    - :attr:`path` The path to the root of the tmQM-RDF directory.  
    - :attr:`index` A dictionary with keys 'centres', 'elements', 'ligands', and 'TMCs' whse values are the lists of the available entries for the corresponding assertions.  
    - :attr:`tbox` An instance of :class:`terminology.TmqmRDFTBoxSubgraph` representing the TBox.  
    - :attr:`t` Alias for :attr:`tbox`.  
    """

    def __init__(self, path):
        """
        :param path: The path to the root dir of tmQM-RDF, i.e., the `<root>` node in the tree
        
        .. code-block :: bash

           <root>
           ├── assertions
           │   └── ...
           └── terminology
               └──  ...
        """
        super().__init__()

        with open(os.path.join(path, ".pages"), "r") as f:
            self._pages = eval(f.read())

        self.no = _pages._LookupEngine(self._pages["version"])
        """The local :doc:`Online Lookup Engine </usage/lookup>`"""

        self.path = os.path.abspath(path)
        """The path to the root of the tmQM-RDF directory."""

        self._raw_index = {
            key: [_tvar for f in os.listdir(os.path.join(self.path, "assertions", key)) if not f.startswith(".") and len(_tvar := f.split(".")) == 2]
            for key in ["centres", "elements", "ligands", "TMCs"]
        }

        self.index = {
            key: [f[0] for f in value]
            for key, value in self._raw_index.items() 
        }
        """A dictionary with keys 'centres', 'elements', 'ligands', and 'TMCs' whse values are the lists of the available entries 
           for the corresponding assertions."""

        extension_type = set(sum([[f[1] for f in val] for val in self._raw_index.values()], []))
        assert len(extension_type) == 1, f"Unable to identify dataset format. Found: {extension_type}; expected EXACTLY one of {list(rdflib.util.SUFFIX_FORMAT_MAP) + ["hdt"]}."

        self._backend = next(iter(extension_type))

        self.tbox = terminology.TmqmRDFTBoxSubgraph(self)
        """An instance of :class:`terminology.TmqmRDFTBoxSubgraph` representing the TBox."""
        self.t = self.tbox
        """Alias for :attr:`tbox`."""
    
    def _read_kgraph(self, rdf_file):
        """
        Reads a knowledge graph in the form of an `rdflib.Graph`_ object using the appropriate backend
        (either rdflib or rdflib_hdt).

        :param rdf_file: The (full) path to the rdf file.
        :return: An `rdflib.Graph`_ instance

        .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
        """
        extension = self._backend
        if extension in rdflib.util.SUFFIX_FORMAT_MAP:
            kgraph = rdflib.Graph()
            kgraph.parse(rdf_file)
        elif extension == "hdt":
            kgraph = rdflib.Graph(store = _TmqmRDF_HDTStore(str(rdf_file), mapped = True))
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
        #out.kgraph.close()
        #out._kgraph = None
        #return out

    def fetch(self, tmcs = [], ligands = [], centres = [], elements = [], auto_fetch_tmc_components = False, progress = True):
        """
        Fetches the requested subgraphs from tmQM-RDF and makes them available for access via dictionary-like syntax.
        For each possible category, objects can be identified via their symbols or via a callable. If the latter is chosen,
        the callable must accept one argument (the parsed object) and return a boolean (whether the object is accepted or not).

        :param tmcs: The list of CSD codes of the desired TMCs, or a callable as described above.
        :param ligands: The list of the tmQMg-L codes of the desired ligands, or a callable as described above.
        :param centres: The list of chemical symbols of the desired metal centres, or a callable as described above.
        :param elements: The list of chemical symbols of the desired elements, or a callable as described above.
        :param auto_fetch_tmc_components: Should the components of all requested TMCs (ligands, metal centres, elements) be automatically fetched? Default: False.
        :param progress: Show a progress bar. Default: True
        """

        objects_symbols = {
            "tmcs": tmcs,
            "ligands": ligands,
            "centres": centres,
            "elements": elements
        }

        categories = [cat for cat in objects_symbols if len(objects_symbols[cat]) > 0]

        for catname in tqdm(categories, disable = not progress):
            # Process category class and symbols list
            objects = objects_symbols[catname]
            Category = {"tmcs": assertions.TMC, "ligands": assertions.Ligand, "centres": assertions.Centre, "elements": assertions.Element}.get(catname)

            criterion = None
            if callable(objects):
                criterion = objects
                objects = self.index[catname if catname != "tmcs" else "TMCs"]

            # Start parsing objects
            preparsed_objects = [(obj, Category) for obj in objects if (Category.category, obj) not in self.data]

            if len(preparsed_objects) == 0:
                continue

            parse = functools.partial(contrib.tmap, disable = not progress, leave = False)

            for obj in parse(self._read, preparsed_objects):
                if criterion is not None and not criterion(obj):
                    continue

                super().__setitem__((Category.category, obj.symbol), obj)
                
                # If needed, run auto_fetch_tmc_components routine
                if auto_fetch_tmc_components and Category.category == "TMC":
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
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components)
    
           return self["TMC", csd_code]
        """
        self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components, progress = False)

        return self["TMC", csd_code]

    def ligand(self, tmqmgl_code):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(ligands = [tmqmgl_code])

           return self["ligand", tmqmgl_code]
        """
        self.fetch(ligands = [tmqmgl_code], progress = False)

        return self["ligand", tmqmgl_code]

    def centre(self, symbol):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(centres = [symbol])
    
           return self["centre", symbol]
        """
        self.fetch(centres = [symbol], progress = False)

        return self["centre", symbol]

    def element(self, symbol):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(elements = [symbol])
    
           return self["element", symbol]
        """
        self.fetch(elements = [symbol], progress = False)

        return self["element", symbol]

    def as_knowledge_graph(self):
        """
        Returns a single `rdflib.Graph`_ RDF graph given by the union of all the fetched subgraphs.

        .. _`rdflib.Graph`: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
        """

        return sum([g.kgraph for g in self.values()], rdflib.Graph())

    def clear(self):
        """
        Utility function that closes all open RDF/HDT documents and clears the internal dictionary.
        """

        for value in self.data.values():
            value.kgraph.close()
        
        self.data = {}

# %% Computing utils ====
def concurrent_map(tmqmrdf_path, job, target, context = None, batchsize = 100, n_workers = 1, **kwargs):
    """
    Processes the entries of tmQM-RDF according to a specified function using `tqdm.contrib.concurrent.process_map`_.

    This function initialises an empty instance of :class:`tmqmrdfdata.TmqmRDF` which is then passed along
    to each worker to enable data access.

    :param:`job` must be a function with two mandatory positional arguments (in order): 
    
    - a :class:`tmqmrdfdata.TmqmRDF` instance;
    - target data (see below);

    and one mandatory keyword argument:

    - *context*: context data (see below);

    Additional keyword arguments are allowed.

    The data passed to the :param:`job` function can be divided in two categories:

    - :param:`target`: the main focus of the job. This is a stream of data points that can be processed independently
        of each other. The stream will be partitioned in batches of size :param:`chuncksize` and then dispatched to
        the workers.
    - :param:`context`: context data that can be useful for the task at hand. This data stream is provided *identically*
        in its entirety to each worker.

    Both target and context data can be provided either as a list of objects or as a string indicating one of the tmQM-RDF
    categories: "TMCs", "ligands", "centres", or "elements", in which case the entirety of the available entry symbols will be loaded.
    For :param:`context`, multiple categories can be specified at once by providing a single string with comma separated category names (whitespaces are ignored).
    If data is specified as category names, the following conversion rules will be applied at runtime: target data will be transformed into a list
    of symbols (strings); context data will be transformed into a dictionary where category names are the keys and the values are lists of symbols (strings).
    Examples of usage are the following:

    .. code-block:: python
        # Target data: subset of TMCs (divided among workers), no context
        tmcs = ["XXYYZZ", "AABBCC", ...]
        concurrent_transform(..., target = tmcs, ...)

        # Target data: subset of TMCs (divided among workers), context: ligands (each worker receives the entire list of ligand symbols)
        tmcs = ["XXYYZZ", "AABBCC", ...]
        concurrent_transform(..., target = tmcs, context = "ligands", ...)

        # Target data: TMCs (divided among workers), context: ligands (each worker receives the entire list of ligand symbols)
        concurrent_transform(..., target = "TMCs", context = "ligands", ...)

        # Target data: TMCs (divided among workers), context: ligands and elements (each worker receives the entire list of ligand and element symbols)
        concurrent_transform(..., target = "TMCs", context = "ligands, elements", ...)

    :param tmqmrdf_path: path to the root of tmQM-RDF.
    :param job: callable, the function to apply to a batch of data. See details above.
    :param target: a list of items to be batched and dispatched to the workers.
    :param context: additional data, each worker receives a copy. Default: None.
    :param batchsize: batch size. Default: 100.
    :param n_workers: number of parallel workers. Default: 1.
    :param kwargs: additional keyword argruments passet to :param:`job`.

    :return: a list where each entry is the result of :param:`job` applied to a batch of :param:`target` data.

    .. _tqdm.contrib.concurrent.process_map: https://tqdm.github.io/docs/contrib.concurrent/#process_map
    """

    tmqmrdf = TmqmRDF(tmqmrdf_path)

    if type(target) == str:
        target = tmqmrdf.index[target]
    target = list(itertools.batched(target, batchsize))

    if type(context) == str:
        context = context.replace(" ", "").split(",")
        context = {
            category: tmqmrdf.index[category]
            for category in context
        }

    out = concurrent.process_map(
        functools.partial(job, tmqmrdf, context = context, **kwargs),
        target,
        max_workers = n_workers,
        chunksize = 1
    )

    return out