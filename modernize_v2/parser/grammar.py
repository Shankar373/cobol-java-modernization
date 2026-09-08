"""T-2B-03 Grammar Classification.

Defines which COBOL constructs are supported in T-2B-03 and which
should be flagged as UNSUPPORTED_FEATURE.

Authoritative table: CONSTRUCT | T-2B-03 STATUS | PARSER BEHAVIOR
See PHASE_2B_T3_IMPLEMENTATION_REPORT.md for full rationale.
"""

from __future__ import annotations

from typing import Final, Tuple, Dict, Set

# ----- Supported constructs (T-2B-03 initial release) -----

# Statement kinds that the parser handles natively
_SUPPORTED_STATEMENTS: Final[Set[str]] = {
    # Simple statements
    "MOVE",
    "DISPLAY",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "DIVIDE",
    "COMPUTE",
    "STOP RUN",
    "GOBACK",
    "EXIT PERFORM",
    "EXIT PARAGRAPH",
    # Control flow
    "GO TO",
    # IF/END-IF family
    "IF",
    "ELSE",
    "END-IF",
    # EVALUATE/WHEN/END-EVALUATE
    "EVALUATE",
    "WHEN",
    "END-EVALUATE",
    # Simple PERFORM
    "PERFORM",
}

# Structural division/section headers recognized by the parser
_SUPPORTED_STRUCTURAL: Final[Set[str]] = {
    "IDENTIFICATION DIVISION",
    "ENVIRONMENT DIVISION",
    "DATA DIVISION",
    "PROCEDURE DIVISION",
}

# ----- Unsupported constructs (T-2B-03 out of scope) -----

_UNSUPPORTED_STATEMENTS: Final[Set[str]] = {
    # SQL
    "EXEC SQL",
    # CICS
    "EXEC CICS",
    # File I/O
    "READ",
    "WRITE",
    "REWRITE",
    "DELETE",
    "START",
    # SORT/MERGE/Report
    "SORT",
    "MERGE",
    "REPORT WRITER",
    # Advanced PERFORM
    "PERFORM VARYING",
    # String/literal handling (lexer conservatively emits numbers as IDENTIFIER)
    "STRING LITERAL",
    # Nested copybooks beyond simple expansion
    "NESTED COPYBOOK",
    # Preprocessor
    "COPY",
    "REPLACE",
    "REPLACING",
}

# Full lookup: construct name -> status
SUPPORTED_LOOKUP: Final[Dict[str, str]] = {}
for s in _SUPPORTED_STATEMENTS:
    SUPPORTED_LOOKUP[s] = "SUPPORTED"
for s in _SUPPORTED_STRUCTURAL:
    SUPPORTED_LOOKUP[s] = "SUPPORTED"
for s in _UNSUPPORTED_STATEMENTS:
    SUPPORTED_LOOKUP[s] = "UNSUPPORTED"


def is_supported(construct: str) -> bool:
    """Return True if *construct* is in the T-2B-03 supported set."""
    return SUPPORTED_LOOKUP.get(construct, "UNSUPPORTED") == "SUPPORTED"


def classify(construct: str) -> str:
    """Return the T-2B-03 status of *construct*.

    One of: "SUPPORTED", "UNSUPPORTED"
    """
    return SUPPORTED_LOOKUP.get(construct, "UNSUPPORTED")


# ------------------------------------------------------------------
# Canonical sets for CI / test use
# ------------------------------------------------------------------

SUPPORTED_STATEMENTS: Final[Tuple[str, ...]] = tuple(_SUPPORTED_STATEMENTS)  # type: ignore
SUPPORTED_STRUCTURAL: Final[Tuple[str, ...]] = tuple(_SUPPORTED_STRUCTURAL)  # type: ignore
UNSUPPORTED_STATEMENTS: Final[Tuple[str, ...]] = tuple(_UNSUPPORTED_STATEMENTS)  # type: ignore


# ------------------------------------------------------------------
# Phrase-level fast‑paths used by the parser
# ------------------------------------------------------------------

# The first token of a statement that the parser dispatches on.
_STATEMENT_FIRST_TOKEN: Final[Dict[str, str]] = {
    "MOVE": "MOVE",
    "DISPLAY": "DISPLAY",
    "ADD": "ADD",
    "SUBTRACT": "SUBTRACT",
    "MULTIPLY": "MULTIPLY",
    "DIVIDE": "DIVIDE",
    "COMPUTE": "COMPUTE",
    "STOP RUN": "STOP RUN",
    "GOBACK": "GOBACK",
    "EXIT PERFORM": "EXIT PERFORM",
    "EXIT PARAGRAPH": "EXIT PARAGRAPH",
    "GO TO": "GO TO",
    "IF": "IF",
    "ELSE": "ELSE",
    "END-IF": "END-IF",
    "EVALUATE": "EVALUATE",
    "WHEN": "WHEN",
    "END-EVALUATE": "END-EVALUATE",
    "PERFORM": "PERFORM",
    "IDENTIFICATION DIVISION": "IDENTIFICATION DIVISION",
    "ENVIRONMENT DIVISION": "ENVIRONMENT DIVISION",
    "DATA DIVISION": "DATA DIVISION",
    "PROCEDURE DIVISION": "PROCEDURE DIVISION",
}

# Phrase starters that are NOT statements but structural.
_STRUCTURAL_FIRST_TOKEN: Final[Dict[str, str]] = {
    "IDENTIFICATION DIVISION": "IDENTIFICATION DIVISION",
    "ENVIRONMENT DIVISION": "ENVIRONMENT DIVISION",
    "DATA DIVISION": "DATA DIVISION",
    "PROCEDURE DIVISION": "PROCEDURE DIVISION",
}