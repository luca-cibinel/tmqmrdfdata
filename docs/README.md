# API References

This is the API documentation of the `tmqmrdfdata` package.

- ![method](https://img.shields.io/badge/method-purple) &nbsp;[tmqmrdfdata.download_tmQM_RDF_knowledge_graph](#-tmqmrdfdatadownload_tmqm_rdf_knowledge_graph): download utility for tmQM-RDF
- ![class](https://img.shields.io/badge/class-turquoise) &emsp;&nbsp;[tmqmrdfdata.TmqmRDF](): main interface to tmQM-RDF
- ![module](https://img.shields.io/badge/module-gray) &ensp;[tmqmrdfdata.terminology](): TBox utilities
- ![module](https://img.shields.io/badge/module-gray) &ensp;[tmqmrdfdata.assertions](): ABox utilities

# tmqmrdfdata methods

## ![method](https://img.shields.io/badge/method-purple) tmqmrdfdata.download_tmQM_RDF_knowledge_graph
```python
def download_tmQM_RDF_knowledge_graph(dir = ".", version = "latest")
```
Downloads the tmQM-RDF knowledge graph from its [GitHub repository](https://github.com/luca-cibinel/tmQM-RDF-archive) using the GitHub REST API.

- **Parameters**:
  - `dir`: the directory where the data should be saved. Default: '.'.
  - `version`: the desired tmQM-RDF version, can be either 'latest' or any other available version number (without leading 'v') as a string. Default: 'latest'.

# tmqmrdfdata classes
## ![class](https://img.shields.io/badge/class-turquoise) tmqmrdfdata.TmqmRDF
```python
class TmQMRDF(collections.UserDict)
```
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
  - `tbox`: an instance of `tmqmrdfdata.terminology.TmqmRDFTBoxSubgraph` representing the TBox.
  - `t`: alias for `tbox`.

### \_\_init\_\_
```python
def __init__(path)
```
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

### fetch
```python
def fetch(tmcs = [], ligands = [], centres = [], elements = [], auto_fetch_tmc_components = False, n_cores = 1)
```
Fetches the requested subgraphs from tmQM-RDF and makes them available for access via dictionary-like syntax.

- **Parameters**:
  - `tmcs`: the list of CSD codes of the desired TMCs.
  - `ligands`: the list of the tmQMg-L codes of the desired ligands.
  - `centres`: the list of chemical symbols of the desired metal centres.
  - `elements`: the list of chemical symbols of the desired elements.
  - `auto_fetch_tmc_components`: should the components of all requested TMCs (ligands, metal centres, elements) be automatically fetched? Default: False.
  - `n_cores`: number of cores to use for import. Default: 1.
 
### tmc
```python
def tmc(csd_code, with_components = False)
```
Wrapper for:
  - (equivalent code)
    ```python
    self.fetch(tmcs = [csd_code], auto_fetch_tmc_components = with_components)
  
    return self["TMC", csd_code]
    ```
 
### ligand
```python
def ligand(tmqmgl_code)
```
Wrapper for:
  - (equivalent code)
    ```python
    self.fetch(ligands = [tmqmgl_code])
  
    return self["ligand", tmqmgl_code]
    ```
 
### centre
```python
def centre(symbol)
```
Wrapper for:
  - (equivalent code)
    ```python
    self.fetch(centres = [symbol])
  
    return self["centre", symbol]
    ```
 
### element
```python
def element(symbol)
```
Wrapper for:
  - (equivalent code)
    ```python
    self.fetch(elements = [symbol])
  
    return self["element", symbol]
    ```

### as_knowledge_graph
```python
def as_knowledge_graph()
```
Returns a single [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) RDF graph given by the union of all the exposed subgraphs

# ![module](https://img.shields.io/badge/module-gray) tmqmrdfdata.terminology

A module dedicated to processing and referencing the terminology component of tmQM-RDF. It serves a dual purpose: it exposes the namespaces used in tmQM-RDF as [rdflib.Namespace](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace/) objects and provides a class that contains all the namespaces and URIs in the tmQM-RDF TBox as attributes, for accessible and quick referencing.

- **Variables**
  - For each prefix `<pfx>` used in tmQM-RDF, a variable `tmqmrdfdata.terminology.<pfx>` is defined as an [rdflib.Namespace](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace/) instance.
 
## tmqmrdfdata.terminology classes

### ![class](https://img.shields.io/badge/class-turquoise) TmQMRDFTBoxSubgraph
```python
class TmQMRDFTBoxSubgraph
```
A convenience class designed to summarise the TBox of tmQM-RDF.

Upon initialisation of TmqmRDF, this class is instantiated as an attribute of the main interface. This class crawls across the knowledge graph collecting all the effective namespaces and URIs defined by the TBox. This mechanism allows to avoid hardwiring the RDF/RDFS terms into the code and allows the package to adapt to potential changes implemented in future versions of the knowledge graph.

- **Attributes**:
  - `kgraph`: the [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) representation of the TBox.
  - `tmqmrdf`: the parent TmqmRDF instance.
  - For each namespaxe `<pfx>` defined in tmQM-RDF, an attribute `.<pfx>` is defined. The value of the attribute is a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) whose attributes are the suffixes of the URIs within the namespace (those attributes evaluate to the corresponding [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) objects).

#### \_\_init\_\_
```python
def __init__(tmqmrdf, category)
```

- **Parameters**:
  - `tmqmrdf`: the parent TmqmRDF instance.

# ![module](https://img.shields.io/badge/module-gray) tmqmrdfdata.assertions
A module designed to handle the individual subgraphs of the tmQM-RDF ABox corresponding to TMCs, ligand species, metal centres, and elements. In addition to exposing the standard functionalities provided by [rdlib](https://rdflib.readthedocs.io/en/stable/), the classes defined in this module allow to easily retrieve all the possible properties of these objects using a [networkx](https://networkx.org/en/)-like syntax.

## tmqmrdfdata.assertions classes

### ![class](https://img.shields.io/badge/class-turquoise) TmqmRDFABoxSubgraph
```python
class TmqmRDFABoxSubgraph
```
A base class representing a subgraph of tmQM-RDF's ABox.

- **Attributes**:
  - `kgraph`: the [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) representation of the TBox.
  - `tmqmrdf`: the parent TmqmRDF instance.
  - `code`: the identifying code (CSD, tmQMg-L, chemical symbol) of the object of interest.
  - `public_code`: alias for `code`.

#### \_\_init\_\_
```python
def __init__(tmqmrdf, category, code)
```

- **Parameters**:
  - `tmqmrdf`: the parent TmqmRDF instance.
  - `category`: one of "TMCs", "ligands", "centres", "elements".
  - `code`: the identifying code (CSD, tmQMg-L, chemical symbol) of the object of interest.
 
#### query
```python
def query(query_object)
```
Wrapper for `self.kgraph.query()`. See [rdflib.Graph.query](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/#rdflib.graph.Graph.query).

### ![class](https://img.shields.io/badge/class-turquoise) TMC
```python
class TMC(TmqmRDFABoxSubgraph)
```
A class representing the subgraph of tmQM-RDF describing a given TMC instance

- **Attributes**
  - `tmc_name`: alias for `self.code`.
  - `CSD_code`: alias for `self.code`.

#### \_\_init\_\_
```python
def __init__(tmqmrdf, tmc_name)
```

- **Parameters**:
  - `tmqmrdf`: the parent TmqmRDF instance.
  - `tmc_name`: the CSD code of the TMC.

#### atoms
```python
def atoms(data = None, alt = "tmQM")
```
Retrieve the list of atoms in the molecular graph of the TMC.

- **Parameters**:
  - `data`: either None, an [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef), or a list of such. If different from None, the given URIs indicate which properties should be retrieved alongside with the list of atoms. URIs must belong to the `tmAp` prefix. Default: None.
  - `alt`: one of "tmQM" or "tmQMg". In case a requested property is specified in both of these datasets, the one coming from the `alt` dataset will be absorbed into an `alt` attribute of the [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) representing the property.
 
- **Returns**:
  - A dictionary where keys are [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representing atoms and values are [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) objects with the following attributes:
    - `symbol`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the chemical symbol of the atom;
    - if properties are requested (via the `data` parameter), an attribute corresponding to the suffix of each requested property. The value of the attribure is a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) mirroring the set of directed paths starting at the URI of the property object in the RDF graph. As a rule of thumb, predicates are turned into attributes of the tuple(s), objects are turned into Python objects if they are URIs/literals, and turned into a nested named tuple if they are blank nodes. Instances of [rdfs:Container](https://www.w3.org/TR/rdf-schema/#ch_containervocab) are an exception, as they are turned in lists where objects are converted again using the same mechanism above. Please refer to the [tmQM-RDF documentation](https://github.com/luca-cibinel/tmQM-RDF).

#### bonds
```python
def bonds(data = None, alt = "tmQM")
```
Retrieve the list of atomic bonds in the molecular graph of the TMC.

- **Parameters**:
  - `data`: either None, an [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef), or a list of such. If different from None, the given URIs indicate which properties should be retrieved alongside with the list of atom bonds. URIs must belong to the `tmBp` prefix. Default: None.
  - `alt`: one of "tmQM" or "tmQMg". In case a requested property is specified in both of these datasets, the one coming from the `alt` dataset will be absorbed into an `alt` attribute of the [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) representing the property.
 
- **Returns**:
  - A dictionary where keys are [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representing bonds and values are [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) objects with the following attributes:
    - `atoms`: the list of the two [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representations of the atoms in the bond;
    - if properties are requested (via the `data` parameter), an attribute corresponding to the suffix of each requested property. The value of the attribure is a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) mirroring the set of directed paths starting at the URI of the property object in the RDF graph. As a rule of thumb, predicates are turned into attributes of the tuple(s), objects are turned into Python objects if they are URIs/literals, and turned into a nested named tuple if they are blank nodes. Instances of [rdfs:Container](https://www.w3.org/TR/rdf-schema/#ch_containervocab) are an exception, as they are turned in lists where objects are converted again using the same mechanism above. Please refer to the [tmQM-RDF documentation](https://github.com/luca-cibinel/tmQM-RDF).

#### ligands
```python
def ligands()
```
Retrieve the list of ligands the TMC.

- **Returns**:
  - A dictionary where keys are [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representing ligands and values are [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) objects with the following attributes:
    - `symbol`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the tmQMg-L code of the ligand species;
    - `atoms`: the list of the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representations of the atoms in the ligand.

#### centre
```python
def centre(as_tuple = True)
```
Retrieve the metal centre of the TMC.

- **Parameters**:
  - `as_tuple`: if True, returns the result as a tuple of the form `(metal_centre_uri, metal_centre_data)` instead of a dictionary of the form `{metal_centre_uri: metal_centre_data}` (added for compatibility with the output of the other functions).

- **Returns**:
  - A tuple/dictionary as described above where:
    - `metal_centre_uri`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the metal centre;
    - `metal_centre_data`: a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) with the following attributes:
      - `symbol`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the metal centre (as a ligand level object);
      - `atoms`: the (singleton) list of the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representation of the metal centre atom.

#### lbonds
```python
def lbonds()
```
Retrieve the list of ligand-metal centre bonds the TMC.

- **Returns**:
  - A dictionary where keys are [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representing ligand-level bonds and values are [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) objects with the following attributes:
    - `ligand`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the ligand participating in the bond;
    - `atoms`: the list of the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representations of the atoms in the ligand bond;
    - `bonds`: the list of the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) representations of the atom-metal centre bonds corresponding to the atoms in `atoms`.

#### complex
```python
def complex(data = None, alt = "tmQM", as_tuple = True)
```
Retrieve the complex-level representation of the TMC.

- **Parameters**:
  - `data`: either None, an [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef), or a list of such. If different from None, the given URIs indicate which properties should be retrieved alongside with the TMC. URIs must belong to the `cmTp` prefix. Note: even if a property is marked in tmQM-RDF as a "meta data", it is treated as any other property by this function. Default: None.
  - `alt`: one of "tmQM" or "tmQMg". In case a requested property is specified in both of these datasets, the one coming from the `alt` dataset will be absorbed into an `alt` attribute of the [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) representing the property.
  - `as_tuple`: if True, returns the result as a tuple of the form `(complex_uri, complex_data)` instead of a dictionary of the form `{complex_uri: complex_data}` (added for compatibility with the output of the other functions).

- **Returns**:
  - A tuple/dictionary as described above where:
    - `complex_uri`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the complex-level representation of the TMC;
    - `complex_data`: a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) with the following attributes:
      - if properties are requested (via the `data` parameter), an attribute corresponding to the suffix of each requested property. The value of the attribure is a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) mirroring the set of directed paths starting at the URI of the property object in the RDF graph. As a rule of thumb, predicates are turned into attributes of the tuple(s), objects are turned into Python objects if they are URIs/literals, and turned into a nested named tuple if they are blank nodes. Instances of [rdfs:Container](https://www.w3.org/TR/rdf-schema/#ch_containervocab) are an exception, as they are turned in lists where objects are converted again using the same mechanism above. Please refer to the [tmQM-RDF documentation](https://github.com/luca-cibinel/tmQM-RDF).

#### skeleton
```python
def skeleton()
```
Computes the "skeleton" of a TMC (i.e. the RDF graph obtained from the corresponding tmQM-RDF entry via a depth-first search, rooted at the TMC node, allowed to move only via URIs) as an auxiliary RDF graph.

- **Returns**:
  - The [rdflib.Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.graph/) of the skeleton.
 
#### as_graphviz
```python
def as_graphviz(layout = "neato")
```
Converts the RDF subgraph into a [graphviz](https://graphviz.readthedocs.io/en/stable/manual.html) graphical representation.

- **Parameters**:
  - `layout`: the desired graphviz layout, one of "dot" or "neato". Default: "neato".

- **Returns**:
  - A [graphviz.Source](https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Source) object.

#### view
```python
def view(self, format = "png", filename = None, layout = "neato"):
```
Produces an image of the TMC rendered via the [graphviz](https://graphviz.readthedocs.io/en/stable/manual.html) module and visualises it.
        
- **Parameters**:
    - `format`: the desired output format for the resulting graphviz object (pdf, png, svg, ...).
    - `filename`: the name of the file (without the extension) to which the output should be saved (optional).
    - `layout`: the desired layout engine, one of '"dot" and "neato". Default: "neato".

#### render
```python
def render(self, format = "png", filename = None, layout = "neato"):
```
Saves an image of the TMC rendered via the [graphviz](https://graphviz.readthedocs.io/en/stable/manual.html) module, without visualising it.
        
- **Parameters**:
    - `format`: the desired output format for the resulting graphviz object (pdf, png, svg, ...).
    - `filename`: the name of the file (without the extension) to which the output should be saved.
    - `layout`: the desired layout engine, one of '"dot" and "neato". Default: "neato".

### ![class](https://img.shields.io/badge/class-turquoise) Ligand
```python
class Ligand(TmqmRDFABoxSubgraph)
```
A class representing the subgraph of tmQM-RDF describing a given ligand species

- **Attributes**
  - `tmqmgl_code`: alias for `self.code`.

#### \_\_init\_\_
```python
def __init__(tmqmrdf, tmqmgl_code)
```

- **Parameters**:
  - `tmqmrdf`: the parent TmqmRDF instance.
  - `tmqmgl_code`: the tmQMg-L code of the species.

#### species
```python
def species(data = None, alt = "tmQM", as_tuple = True)
```
Retrieve the RDF representation of the ligand species.

- **Parameters**:
  - `data`: either None, an [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef), or a list of such. If different from None, the given URIs indicate which properties should be retrieved. URIs must belong to the `lgLrp` prefix. Default: None.
  - `alt`: ignored. Added for compatibility with the other functions.
  - `as_tuple`: if True, returns the result as a tuple of the form `(species_uri, species_data)` instead of a dictionary of the form `{species_uri: species_data}` (added for compatibility with the output of the other functions).

- **Returns**:
  - A tuple/dictionary as described above where:
    - `species_uri`: the [rdflib.term.URIRef](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.term/#rdflib.term.URIRef) of the RDF representation of the species;
    - `species_data`: a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) with the following attributes:
      - if properties are requested (via the `data` parameter), an attribute corresponding to the suffix of each requested property. The value of the attribure is a [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple) mirroring the set of directed paths starting at the URI of the property object in the RDF graph. As a rule of thumb, predicates are turned into attributes of the tuple(s), objects are turned into Python objects if they are URIs/literals, and turned into a nested named tuple if they are blank nodes. Instances of [rdfs:Container](https://www.w3.org/TR/rdf-schema/#ch_containervocab) are an exception, as they are turned in lists where objects are converted again using the same mechanism above. Please refer to the [tmQM-RDF documentation](https://github.com/luca-cibinel/tmQM-RDF).

### ![class](https://img.shields.io/badge/class-turquoise) Centre
```python
class Centre(TmqmRDFABoxSubgraph)
```
A class representing the subgraph of tmQM-RDF describing a given metal centre species.

- **Attributes**
  - `symbol`: alias for `self.code`.

#### \_\_init\_\_
```python
def __init__(tmqmrdf, symbol)
```

- **Parameters**:
  - `symbol`: the chemical symbol of the metal centre.  

### ![class](https://img.shields.io/badge/class-turquoise) Element
```python
class Element(TmqmRDFABoxSubgraph)
```
A class representing the subgraph of tmQM-RDF describing a given element.

- **Attributes**
  - `symbol`: alias for `self.code`.

#### \_\_init\_\_
```python
def __init__(tmqmrdf, symbol)
```

- **Parameters**:
  - `symbol`: the chemical symbol of the element.
