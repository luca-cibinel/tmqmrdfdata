"""
A conveniency module designed to handle lookup of individual .ttl file from the remote GitHub repositories
containing the copies of tmQM-RDF downloadable via :meth:`tmqmrdfdata.download_tmQM_RDF_knowledge_graph`.

Lookup is performed by opening the requested documents in the default web browser.

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

import webbrowser
import rdflib

from . import terminology
from . import assertions

class _LookupEngine:

    BASE_LINK = "https://github.com/luca-cibinel/tmQM-RDF-archive/blob"

    def __init__(self, version = None):
        self.version = version

    def __floordiv__(self, other):
        if type(other) == str:
            loc_version, box, uripath, tail = self._parse_string_params(other)
        else:
            loc_version, box, uripath, tail = self._parse_obj_params(other)

        url = "/".join([self.BASE_LINK, loc_version, box, uripath, f"{tail}.ttl"])
        webbrowser.open_new_tab(url)

    def _parse_string_params(self, path_param):
        params = path_param.split("/")

        loc_version = self.version
        error_token = ""
        if self.version is None:
            error_token = "<version> / "
            loc_version = f"v{params[0]}" if not params[0].startswith("v") else params[0]
            params = params[1:]

        ns_check = False
        box = None
        match params[0]:
            case "TMC":
                box = "assertions"
                uripath = "TMCs"
                tail = assertions.TMC.code(params[-1])
            case "ligand":
                box = "assertions"
                uripath = "ligands"
                tail = assertions.Ligand.code(params[-1])
            case "centre":
                box = "assertions"
                uripath = "centres"
                tail = assertions.Centre.code(params[-1])
            case "element":
                box = "assertions"
                uripath = "elements"
                tail = assertions.Element.code(params[-1])
            case _:
                ns_check = params[0] in terminology.DEFAULT_NAMESPACES
                if ns_check:
                    box = "terminology"
                    uripath = terminology.DEFAULT_NAMESPACES[params[0]].split("#")[1][1:-1]
                    tail = params[-1]
        
        if box is None:
            error_message = "Malformed path parameter. Verify that the following conditions are met:\n"
            error_message += f"\t - expected either `// {error_token}<TMC |ligand | centre | element> / <symbol>` or `// {error_token}<namespace prefix>`. Received: {path_param}.\n"
            error_message += f"\t - if querying using a namespace prefix, the prefix must be defined in tmqmrdfdata.terminology.DEFAULT_NAMESPACES. {params[0]!r} in DEFAULT_NAMESPACES: {ns_check}"
            raise RuntimeError(
                    error_message
                )
    
        return loc_version, box, uripath, tail

    def _parse_obj_params(self, obj):
        if isinstance(obj, assertions.TmqmRDFABoxSubgraph):
            box = "assertions"
            uripath = obj.category + "s"
            tail = obj.code(obj.symbol)
            loc_version = obj.tmqmrdf._pages["version"]
        elif isinstance(obj, rdflib.Namespace):
            box = "terminology"
            uripath = obj.split("#")[1][1:-1]
            tail = terminology.DEFAULT_PREFIXES[obj]
            loc_version = self.version

            if self.version is None:
                raise RuntimeError("rdflib.Namespace-based lookup cannot be performed from the global tmqmrdfdata.no engine.")
        else:
            raise TypeError(f"Object type not recognised: {type(obj)}. Unable to form a path. Acceptable objects are tmqmrdfdata.assertions.TmqmRDFABoxSubgraph and rdflib.Namespace.")
        
        return loc_version, box, uripath, tail

"""
tmrdf.no // "v1.0.1/TMC/ABEVAH"

d.no // ABEVAH
"""