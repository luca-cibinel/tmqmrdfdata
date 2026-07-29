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
    "assertions",
    "factory"
]

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
        f.write(f"https://github.com/luca-cibinel/tmQM-RDF-archive/%s/{vname}/")

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
    
    Due to the size of tmQM-RDF, not all subgraphs are immediately loaded upon class instantiation. The desired subgraphs have to be fetched using the :meth:`fetch` method. For quick access
    to single TMCs, ligand species or elements, the methods :meth:`tmc`, :meth:`ligand`, :meth:`centre`, or :meth:`element` can also be used.

    Each subgraph (the value returned by `self[<category>, <code>]`) is an instance of :class:`assertions.TmqmRDFABoxSubgraph`, and exposes its rdf triples via the :attr:`assertions.TmqmRDFABoxSubgraph.kgraph` attribute, which is
    an `rdflib.Graph`_ object. Each category has unique attributes and dedicated methods to quickly retrieve properties and/or visualise the corresponding chemical object. See the related documentation.

    .. _rdflib.Graph: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/

    The class has the following attributes:

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
            self._pages = f.read().strip()

        self.path = path
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

        self._categories = {
            "tmcs": (assertions.TMC, True, "TMCs"),
            "ligands": (assertions.Ligand, True, "ligands"),
            "centres": (assertions.Centre, True, "centres"),
            "elements": (assertions.Element, True, "elements")
        }

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

    def fetch(self, tmcs = [], ligands = [], centres = [], elements = [], auto_fetch_tmc_components = False, n_cores = 1, **kwargs):
        """
        Fetches the requested subgraphs from tmQM-RDF and makes them available for access via dictionary-like syntax.
        For each possible category, objects can be identified via their symbols or via a callable. If the latter is chosen,
        the callable must accept one arguments (the parsed object) and return a boolean (whether the object is accepted or not).

        :param tmcs: The list of CSD codes of the desired TMCs, or a callable as described above.
        :param ligands: The list of the tmQMg-L codes of the desired ligands, or a callable as described above.
        :param centres: The list of chemical symbols of the desired metal centres, or a callable as described above.
        :param elements: The list of chemical symbols of the desired elements, or a callable as described above.
        :param auto_fetch_tmc_components: Should the components of all requested TMCs (ligands, metal centres, elements) be automatically fetched? Default: False.
        :param n_cores: Number of cores to use for import. Default: 1.
        :param kwargs: For each custom category defined via self.register_category, the list of desired symbols, or a callable as described above.
        """

        objects_symbols = {
            "tmcs": tmcs,
            "ligands": ligands,
            "centres": centres,
            "elements": elements
        } | kwargs

        categories = ["tmcs", "ligands", "centres", "elements"] + list(kwargs.keys())

        for catname in categories:
            # Process category class and symbols list
            objects = objects_symbols[catname]
            Category = self._categories[catname][0]

            criterion = None
            if callable(objects):
                if not self._categories[catname][1]:
                    raise ValueError(f"Category {catname!r} cannot be indexed by a callable!")

                criterion = objects
                objects = self._categories[catname][2]

                if type(objects) is str:
                    objects = self.index[objects]

            # Start parsing objects (possibly in parallel)
            with multiprocessing.Pool(processes = n_cores) as pool:
                parsed_objects = [(obj, Category) for obj in objects if (Category.category, obj) not in self.data]

                if len(parsed_objects) == 0:
                    continue

                if n_cores > 1:
                    parse = pool.imap_unordered
                else:
                    parse = map

                for obj in parse(self._read, parsed_objects):
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

    def register_category(self, category_class, argname = None, fetch_via_callable = False, default_symbols = None):
        """
        Register a subclass of :class:`factory.AbstractTmqmRDFABoxSubgraph` as a viable interface accessibe from :meth:`fetch`.

        :param category_class: A subclass of :class:`factory.AbstractTmqmRDFABoxSubgraph`.
        :param argname: A name for the argument of :meth:`fetch` specifying the symbols to be passed to the class constructor. If None, defaults to ``category_class + 's'``. Default: None.
        :param fetch_via_callable: Whether to allow a callable to be passed to :meth:`fetch` in place of a list of symbols. If True, ``default_symbols`` must also be provided. Default: False.
        :param default_symbols: A list of default symbols to be parsed in case in which a callable is passed to :meth:`fetch`. Can also be a string, one of ``TMCs``, ``ligands``, ``elements``, or ``centres``, in which case the default list is taken to be the full list of available symbols for that class. Must be provided if ``fetch_via_callable`` is True. Ignored if ``fetch_via_callable`` is False. Default: None.
        """
        if argname is None:
            argname = category_class.category + "s"

        if argname in self._categories:
            raise ValueError(f"A category with argname {argname!r} is already registered!")

        if fetch_via_callable and default_symbols is None:
            raise ValueError("A default list of symbols must be provided to 'default_symbols' when 'fetch_via_callable' is True!")

            try:
                iter(default_symbols)

                if type(default_symbols) is str:
                    if default_symbols not in self.index:
                        raise ValueError(f"If 'default_symbols' is a string, it must be one of {list(self.index.keys())}!")

                    default_symbols = self.index[default_symbols]
            except TypeError:
                raise TypeError("'default_symbols' must be either a string or an iterable of symbols!")

        self._categories[argname] = (category_class, fetch_via_callable, default_symbols)
    
    def unregister_category(self, argname):
        """
        Unregister a previously registered interface class.

        :param argname: The argname of the class to unregister.
        """
        if argname in ["tmcs", "elements", "ligands", "centres"]:
            raise ValueError("Cannot unregister a default category!")

        del self._categories[argname]

    def registered_categories(self, label_defaults = False):
        """
        Yields an iterator over descriptive tokens representing the registered categories. Such tokens are tuples of the form::

            (argname, interface class, fetch_via_callable, name/len of default symbols list).

        :param label_defaults: if True, a fifth element is added to each tuple, representing whether that category is a default category. Default: False
        """
        for argname, cat_data in self._categories.items():
            if label_defaults:
                yield (
                    argname, 
                    cat_data[0], 
                    cat_data[1], 
                    cat_data[2] if (type(cat_data[2]) is str or cat_data[2] is None) else len(cat_data[2]),
                    argname in ["tmcs", "elements", "ligands", "centres"]
                )
            else:
                yield (
                    argname, 
                    cat_data[0], 
                    cat_data[1], 
                    cat_data[2] if (type(cat_data[2]) is str or cat_data[2] is None) else len(cat_data[2])
                )

    def tmc(self, csd_code, with_components = False):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components)
    
           return self["TMC", csd_code]
        """
        self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components)

        return self["TMC", csd_code]

    def ligand(self, tmqmgl_code):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(ligands = [tmqmgl_code])

           return self["ligand", tmqmgl_code]
        """
        self.fetch(ligands = [tmqmgl_code])

        return self["ligand", tmqmgl_code]

    def centre(self, symbol):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(centres = [symbol])
    
           return self["centre", symbol]
        """
        self.fetch(centres = [symbol])

        return self["centre", symbol]

    def element(self, symbol):
        """
        Wrapper for the equivalent code:

        .. code-block :: python
           
           self.fetch(elements = [symbol])
    
           return self["element", symbol]
        """
        self.fetch(elements = [symbol])

        return self["element", symbol]

    def as_knowledge_graph(self):
        """
        Returns a single `rdflib.Graph`_ RDF graph given by the union of all the fetched subgraphs.

        .. _`rdflib.Graph`: https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/
        """

        return sum([g.kgraph for g in self.values()], rdflib.Graph())