# Modules

```sova
import tools.parser
import tools.parser as Parser
from tools.parser import parse
from tools.parser import parse as parseSource

export function parse(code) {
    return code
}
```

Module names map to local `.sova` paths such as `tools/parser.sova`. The loader normalizes paths, rejects absolute paths and traversal, builds a dependency graph, caches completed modules, and reports circular imports. Online execution resolves modules only from the submitted in-memory project map.

Standard namespaces such as `Sova.Math` are built in and do not load local files.
