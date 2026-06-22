"""
A module providing utilities for the abstract definition of interfaces to the tmQM-RDF ABox.
It relies on Python's abc module to define an abstract ABox-subgraph class, implemented
by the classes in the `assertions` module and that can also be used to define custom interfaces.

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

from pathlib import Path

import os
import abc

class AbstractTmqmRDFABoxSubgraph(abc.ABC):
    """
    An abstract base class for an ABox interface.

    Classes meant to acces the ABox of tmQM-RDF should extend this class.
    Subclasses of this class must posses the following:
        - an __init__ method accepting *exactly* two arguments: `tmqmrdfd`, an instance of TmqmRDF, and `symbol`, a
            string representing the specific assertions to be extracted. The symbol will be stored in the attributes `code` and
            `public_code`. Unless overridden, `code` is alias for `public_code`.
        - a `kgraph` property, returning the knowledge graph represented by the instance of the class.
        - a `name` class attribute, declaring the code-level name of the type of knowledge accessed by this class.
    The retrieved knowledge graph can be accessed from the tmqmrdf object via the key (`name`, `public_code`).
    """

    def __init__(self, tmqmrdf, symbol):
        self.tmqmrdf = tmqmrdf
        self.code = symbol
        self.public_code = symbol

    @property
    @abc.abstractmethod
    def kgraph(self):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass

def read_kgraph_file(tmqmrdf, rpath, symbol):
    """
    Reads a knowledge graph from the file specified by the
    path relative to the root of the current tmQM-RDF instance. The graph
    is read using the appropriate backend registered within tmqmrdf.

    - Parameters:
        - `tmqmrdf`: the instance of TmqmRDF representing the copy of tmQM-RDF
            from which the file should be read
        - `rpath`: the path of the folder containing the file, relative to the tmQM-RDF root
        - `symbol`: the name, without extension, of the file containing the knowledge graph
    
    - Returns:
        - an rdflib.Graph object
    """
    fpath = Path(os.path.join(tmqmrdf.path, rpath, f"{symbol}.{tmqmrdf._backend}")).absolute()

    return tmqmrdf._read_kgraph(fpath)

def simple_tmqmrdf_abox_interface(name, kgraph_factory):
    """
    A convenience factory for a subclass of factory.AbstractTmqmRDFABoxSubgraph with a customised knowledge graph
    retrieval system but no additional methods.

    - Parameters:
        - `name`: the code-level name of the type of knowledge accessed by this class.
        - `kgraph_factory`: a callable accepting two arguments; i.e., `tmqmrdfd`, an instance of TmqmRDF, and `symbol`, a
            string representing the specific assertions to be extracted

    - Returns:
        - A subclass of factory.AbstractTmqmRDFABoxSubgraph
    """
    class SimpleTmqmRDFABoxSubgraph(AbstractTmqmRDFABoxSubgraph):
        name = name

        def __init__(self, tmqmrdf, symbol):
            self._kgraph = kgraph_factory(tmqmrdf, symbol)
        
        @property
        def kgraph(self):
            return self._kgraph

    return SimpleTmqmRDFABoxSubgraph
