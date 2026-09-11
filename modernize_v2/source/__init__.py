"""modernize_v2.source — Source workspace and source map.

Phase 2B (T-2B-01 only). Phase 2B-02+ (lexer, parser, preprocessor)
is intentionally NOT implemented in this ticket.

The module owns:

    * ``PathSecurityError`` — raised when a path is unsafe
      (traversal, absolute escape, control characters).
    * ``FileKind`` — coarse source-file classification.
    * ``SourceFile`` — an immutable, content-hashed source file.
    * ``SourceMap`` — byte-offset to ``(line, column)`` translation.
    * ``Workspace`` — an immutable collection of ``SourceFile``s
      that exposes deterministic file IDs and rejects unsafe paths.

The workspace does not embed parser behavior. It does not read
COBOL grammar. It does not depend on the V1 lexer. It is
infrastructure for the future lexer and parser.
"""

from __future__ import annotations

from .workspace import (
    FileKind,
    PathSecurityError,
    SourceFile,
    Workspace,
    WorkspaceError,
    make_source_file,
    normalize_canonical_path,
    resolve_relative_path,
)
from .source_map import SourceMap, SourceMapError, byte_to_position

__all__ = [
    "FileKind",
    "PathSecurityError",
    "SourceFile",
    "SourceMap",
    "SourceMapError",
    "Workspace",
    "WorkspaceError",
    "byte_to_position",
    "make_source_file",
    "normalize_canonical_path",
    "resolve_relative_path",
]
