"""COBOL reserved-word / keyword set for the V2 lexer.

This is the *lexical* classification table. Membership here only
affects whether an alphabetic token is emitted as
``TokenKind.KEYWORD`` instead of ``TokenKind.IDENTIFIER``. It
does not imply grammatical acceptability anywhere — that is a
parser concern (T-2B-04).

Rules for this table:

    * One word per entry. COBOL reserved words are single
      tokens; phrases such as "LENGTH OF" are *two* tokens and
      must never appear here as one entry.
    * No duplicates. Duplication would be silently collapsed by
      the frozenset and would hide editing mistakes; they are
      forbidden.
    * Uppercase canonical form. Lookup is case-insensitive via
      ``is_keyword``.
    * The set is ISO COBOL-85/2002 reserved words plus narrowly
      chosen GnuCOBOL extensions actually used in target
      repositories. Words that are not COBOL reserved words
      (vendor schedulers, host utilities, display attributes
      that are identifiers) are deliberately excluded.

The set is deliberately a plain frozenset of strings. It has no
behavior of its own and no hidden IO.
"""

from __future__ import annotations

import re
from typing import Final


_KEYWORD_WORDS: Final[tuple[str, ...]] = (
    # ---- Divisions, sections, declaratives ----------------------
    "IDENTIFICATION", "ENVIRONMENT", "DATA", "PROCEDURE",
    "DIVISION", "SECTION", "CONFIGURATION",
    "SOURCE-COMPUTER", "OBJECT-COMPUTER", "SPECIAL-NAMES",
    "REPOSITORY", "INPUT-OUTPUT", "FILE-CONTROL", "I-O-CONTROL",
    "WORKING-STORAGE", "LOCAL-STORAGE", "LINKAGE", "REPORT",
    "SCREEN", "FILE", "FD", "SD", "RD", "CD",
    "DECLARATIVES", "USE", "DEBUGGING",

    # ---- Program identification ---------------------------------
    "PROGRAM-ID", "AUTHOR", "INSTALLATION", "DATE-WRITTEN",
    "DATE-COMPILED", "SECURITY", "REMARKS",

    # ---- Data description entries --------------------------------
    "PIC", "PICTURE", "USAGE", "VALUE", "VALUES", "REDEFINES",
    "RENAMES", "OCCURS", "DEPENDING", "ASCENDING", "DESCENDING",
    "INDEXED", "KEY", "BLANK", "JUSTIFIED", "JUST", "SIGN",
    "LEADING", "TRAILING", "SEPARATE", "CHARACTER", "CHARACTERS",
    "SYNCHRONIZED", "SYNC", "FILLER",
    "BINARY", "PACKED-DECIMAL", "COMPUTATIONAL", "COMP",
    "COMP-1", "COMP-2", "COMP-3", "COMP-4", "COMP-5",
    "POSITIVE", "NEGATIVE",

    # ---- Figurative constants ------------------------------------
    "ZERO", "ZEROES", "ZEROS", "SPACE", "SPACES",
    "HIGH-VALUE", "HIGH-VALUES", "LOW-VALUE", "LOW-VALUES",
    "QUOTE", "QUOTES", "ALL", "NULL", "NULLS",

    # ---- Control flow verbs ---------------------------------------
    "ACCEPT", "ADD", "ALTER", "CALL", "CANCEL", "CLOSE",
    "COMPUTE", "CONTINUE", "DELETE", "DISPLAY", "DIVIDE",
    "EVALUATE", "EXIT", "GENERATE", "GO", "GOBACK", "IF",
    "INITIALIZE", "INITIATE", "INSPECT", "MERGE", "MOVE",
    "MULTIPLY", "OPEN", "PERFORM", "READ", "RECEIVE",
    "RELEASE", "RETURN", "REWRITE", "SEARCH", "SEND", "SET",
    "SORT", "START", "STOP", "STRING", "SUBTRACT", "SUPPRESS",
    "TERMINATE", "UNSTRING", "UNLOCK", "WRITE",

    # ---- Connectives, clauses, relationals ------------------------
    "AFTER", "ALSO", "AND", "ANY", "ARE", "AS", "AT", "BEFORE",
    "BOTTOM", "BY", "COMMA", "COMMON", "CONTAINS", "CONTENT",
    "CORR", "CORRESPONDING", "COUNT", "DELIMITED", "DELIMITER",
    "DOWN", "ELSE", "END-IF", "END-READ", "END-ADD", "END-CALL",
    "END-COMPUTE", "END-DELETE", "END-DIVIDE", "END-EVALUATE",
    "END-MULTIPLY", "END-OF-PAGE", "EOP", "END-PERFORM",
    "END-RETURN", "END-REWRITE", "END-SEARCH", "END-START",
    "END-STRING", "END-SUBTRACT", "END-UNSTRING", "END-WRITE",
    "EQUAL", "EQUALS", "ERROR", "EVERY", "EXCEPTION", "FALSE",
    "FIRST", "FOR", "FROM", "GIVING", "GREATER", "HEADING",
    "IN", "INTO", "INVALID", "IS", "LAST", "LESS", "LIMIT",
    "LIMITS", "NEXT", "NO", "NOT", "OF", "OFF", "ON", "OR",
    "OTHER", "OVERFLOW", "PAGE", "RECORD", "RECORDS",
    "REMAINDER", "REPLACING", "RESET", "RETURNING", "REVERSED",
    "ROUNDED", "RUN", "SENTENCE", "SIZE", "STANDARD",
    "STANDARD-1", "STANDARD-2", "STATUS", "SUM", "TABLE",
    "TALLYING", "TEST", "THAN", "THEN", "THROUGH", "THRU",
    "TO", "TRUE", "UNDERLINE", "UNTIL", "UP", "UPON", "USING",
    "WHEN", "WITH", "WORDS",

    # ---- File organization / access --------------------------------
    "ACCESS", "ADVANCING", "ALTERNATE", "AREA", "AREAS", "ASSIGN",
    "BLOCK", "CODE-SET", "COLLATING", "CONVERSION", "DYNAMIC",
    "END-CLOSE", "EXTEND", "FILE-LIMIT", "FILE-LIMITS", "I-O",
    "INPUT", "LABEL", "LINE", "LINE-COUNTER", "LINES", "LINKAGE-SPEC",
    "LOCK", "MODE", "MULTIPLE", "ORGANIZATION", "OUTPUT", "PADDING",
    "PARAGRAPH", "POSITION", "RANDOM", "RELATIVE", "RESERVE",
    "SEQUENTIAL", "SHARING", "STATEMENT", "TAPE", "UNIT", "VARYING",

    # ---- String handling --------------------------------------------
    "POINTER", "POINTER-32", "REFERENCE", "REFERENCES",
    "STRING-CX", "EXAMINE", "INSPECT-TALLYING",

    # ---- Environment / special names ------------------------------
    "ADDRESS", "ALPHABET", "ARGUMENT-NUMBER", "ARGUMENT-VALUE",
    "CLS", "COBOL", "CODE", "COLUMN", "COMMAND-LINE", "CONSOLE",
    "CRT", "CURRENCY", "CURRENT-DATE", "DAY", "DAY-OF-WEEK",
    "DECIMAL-POINT", "EDITED", "ENTRY", "ESCAPE", "FOOTING",
    "GROUP", "INDEX", "INVOKE", "LEFT", "LENGTH", "NATIONAL",
    "NUMERIC", "NUMERIC-EDITED", "PRINT", "PRINTER", "PROGRAM",
    "PROGRAM-STATUS", "REMARK", "RIGHT", "SAME", "SCROLL",
    "SKIP1", "SKIP2", "SKIP3", "SORT-MERGE", "SOURCE", "SUB-QUEUE-1",
    "SUB-QUEUE-2", "SUB-QUEUE-3", "SWITCH",
    "SYMBOLIC", "SYSERR", "SYSIN", "SYSLIST", "SYSLST", "SYSOUT",
    "TERMINAL", "TIME", "TOP", "TYPE",

    # ---- COBOL 2002 / OO subset recognised by mainframe compilers --
    "CLASS", "CLASS-ID", "END-INVOKE", "FACTORY", "INHERITS",
    "INTERFACE", "INTERFACE-ID", "METHOD", "METHOD-ID", "OBJECT",
    "OVERRIDE", "PROPERTY", "RAISE", "SELF", "SUPER",

    # ---- GnuCOBOL extensions accepted by real repositories ---------
    "FUNCTION", "INITIAL", "PROCEED", "RECURSIVE",
    "RETURN-CODE", "STANDARD-DEVIATION", "UNBOUNDED", "XLATE",
    "BIT", "BOOLEAN", "ANYNUM",
)


_KEYWORDS: Final[frozenset[str]] = frozenset(_KEYWORD_WORDS)


_WORD_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9-]*$")


def _validate_keyword_set() -> None:
    """Fail-closed validation of the keyword table.

    Called inline at import time so that the module can never
    be used with a malformed table.
    """
    seen: set[str] = set()
    for word in _KEYWORDS:
        if " " in word:
            raise AssertionError(
                f"multi-word entry in keyword table: {word!r}; "
                "COBOL reserved words are single tokens"
            )
        if not _WORD_RE.match(word):
            raise AssertionError(
                f"invalid keyword spelling: {word!r}; keywords are "
                "UPPERCASE letters, digits, and hyphens"
            )
        if word in seen:
            raise AssertionError(f"duplicate keyword: {word!r}")
        seen.add(word)


_validate_keyword_set()


def is_keyword(word: str) -> bool:
    """True if ``word`` (any case) is a COBOL reserved word."""
    if not isinstance(word, str) or not word:
        return False
    return word.upper() in _KEYWORDS


def keyword_count() -> int:
    """Number of keywords in the table (diagnostics)."""
    return len(_KEYWORDS)


__all__ = ["is_keyword", "keyword_count"]
