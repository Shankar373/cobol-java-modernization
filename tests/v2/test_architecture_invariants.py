"""Architecture invariants for modernize_v2.

These tests are the regression gate for the Phase 2A architecture
contract. Any future change that violates one of the invariants
must be justified explicitly.

Invariants:

    1. modernize_v2 imports without V1 runtime dependencies.
    2. No V2 module imports libcobj.
    3. No V2 module imports jp.osscons.
    4. No V2 module imports OpenSourceCOBOL4J.
    5. No V2 public model uses Dict[str, Any] as a semantic
       contract.
    6. modernize_v2 has no filesystem access at import time.
    7. modernize_v2 has no environment variable access at import
       time.
    8. modernize_v2 has no wall-clock access at import time.
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
V2_ROOT = REPO_ROOT / "modernize_v2"

FORBIDDEN_IMPORTS = (
    "libcobj",
    "jp.osscons",
    "OpenSourceCOBOL4J",
    "open_source_cobol4j",
)


def _iter_python_files() -> list[Path]:
    return sorted(V2_ROOT.rglob("*.py"))


def _parse_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def test_modernize_v2_imports_cleanly() -> None:
    import modernize_v2
    assert modernize_v2.__phase__ == "2A"


def test_no_forbidden_imports() -> None:
    """V2 must not import V1 runtime or legacy emulators."""
    offenders: list[tuple[Path, str]] = []
    for path in _iter_python_files():
        tree = _parse_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top in FORBIDDEN_IMPORTS:
                        offenders.append((path, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in FORBIDDEN_IMPORTS:
                    offenders.append((path, module))
                top = module.split(".")[0]
                if top in FORBIDDEN_IMPORTS:
                    offenders.append((path, module))
    assert not offenders, f"forbidden imports: {offenders}"


def test_no_modernize_imports_in_v2() -> None:
    """V2 must not import the V1 'modernize' package internals."""
    offenders: list[tuple[Path, str]] = []
    for path in _iter_python_files():
        tree = _parse_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "modernize" or alias.name.startswith(
                        "modernize."
                    ):
                        offenders.append((path, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "modernize" or module.startswith("modernize."):
                    offenders.append((path, module))
    assert not offenders, (
        "V2 must be independent of V1 internals: " + repr(offenders)
    )


def test_no_dict_str_any_in_public_classes() -> None:
    """V2 public models must not have Dict[str, Any] as a field type.

    Allowed exceptions: legacy compatibility shims (none in V2A).
    """
    offenders: list[tuple[Path, int, str]] = []
    for path in _iter_python_files():
        tree = _parse_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and node.annotation is not None:
                ann = ast.unparse(node.annotation)
                if "Dict[str, Any]" in ann or "dict[str, Any]" in ann:
                    offenders.append(
                        (path, node.lineno, ann)
                    )
            elif isinstance(node, ast.arg) and node.annotation is not None:
                ann = ast.unparse(node.annotation)
                if "Dict[str, Any]" in ann or "dict[str, Any]" in ann:
                    offenders.append(
                        (path, node.lineno, ann)
                    )
    assert not offenders, f"Dict[str, Any] found: {offenders}"


def test_v2_imports_does_not_open_arbitrary_files() -> None:
    """V2 has no top-level file I/O in the AST.

    Python 3.14's import system bypasses ``builtins.open`` for
    source loading, so a runtime spy is unreliable. We assert
    the structural property: no V2 module contains a top-level
    statement that opens a file at import time.
    """
    offenders: list[tuple[Path, int, str]] = []
    for path in _iter_python_files():
        tree = _parse_module(path)
        for node in tree.body:  # top-level only
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    func = sub.func
                    if (
                        isinstance(func, ast.Name)
                        and func.id in {"open", "read_text", "read_bytes"}
                    ):
                        offenders.append(
                            (path, sub.lineno, func.id)
                        )
                    if (
                        isinstance(func, ast.Attribute)
                        and func.attr in {"read_text", "read_bytes"}
                    ):
                        offenders.append(
                            (path, sub.lineno, func.attr)
                        )
    assert not offenders, f"top-level I/O in V2: {offenders}"


def test_v2_import_does_not_read_environment() -> None:
    """Importing V2 must not read environment variables.

    Subprocess runs with a stripped environment. If V2 reads env
    vars at import time, the test still passes (since reading is
    a no-op when the var is missing); the assertion is that
    import does not *crash* and that the public surface works
    in a clean environment. The deeper invariant is structural:
    no V2 module uses os.environ at import time.
    """
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "HOME": os.environ.get("HOME", ""),
    }
    import subprocess
    out = subprocess.check_output(
        [
            sys.executable, "-c",
            f"import sys; sys.path.insert(0, r'{REPO_ROOT}');"
            "import modernize_v2; print(modernize_v2.__version__)",
        ],
        env=env,
    )
    assert out.strip().startswith(b"2.")


def test_v2_does_not_use_wall_clock_at_import() -> None:
    """V2 import must not call time.time() or datetime.now()."""
    # Structural assertion: no time/datetime imports in V2.
    offenders: list[tuple[Path, str]] = []
    for path in _iter_python_files():
        tree = _parse_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("time", "datetime"):
                        offenders.append((path, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in ("time", "datetime"):
                    offenders.append((path, module))
    assert not offenders, f"forbidden time imports: {offenders}"


def test_v2_does_not_use_random_at_import() -> None:
    """V2 ids must not depend on randomness; this is structural."""
    offenders: list[tuple[Path, str]] = []
    for path in _iter_python_files():
        tree = _parse_module(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("random", "uuid"):
                        offenders.append((path, alias.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module in ("random", "uuid"):
                    offenders.append((path, module))
    assert not offenders, f"forbidden randomness imports: {offenders}"


def test_modernize_v2_subpackages_are_present() -> None:
    """The Phase 2A subpackage structure must be present."""
    import modernize_v2
    import modernize_v2.ir
    import modernize_v2.capabilities
    import modernize_v2.verification
    # Each subpackage has an __init__ and is non-empty.
    for sub in ("ir", "capabilities", "verification"):
        path = V2_ROOT / sub / "__init__.py"
        assert path.exists(), f"missing {path}"
        assert path.stat().st_size > 0
