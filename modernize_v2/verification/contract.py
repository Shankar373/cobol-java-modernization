"""V2 VerificationContract.

The contract declares what a differential comparison must check
and how. It is the only place where the comparison mode for
each dimension is set; the comparator does not pick a mode
heuristically.

A contract declares:

    * the workload identity
    * which observation dimensions are required
    * the comparison mode per dimension
    * the encoding
    * the seed declarations (explicit, allow-listed)
    * the expected artifact set
    * the verification policy and version

If a required dimension is absent from an observation, the
verdict is ``UNVERIFIED`` (not ``PASS``). If the contract is
invalid, the pipeline raises ``ContractValidationError`` and
refuses to continue.

The contract is immutable. The seed declarations are *data*, not
executable scripts; V2 does not auto-execute ``data/*.sql``
files. The executor (Phase 2K) accepts only ``INSERT INTO`` and
``MERGE INTO`` against declared tables.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final, Mapping

from .observation import ALL_DIMENSIONS, Encoding


class ComparisonMode(str, Enum):
    """The mode for comparing a single dimension.

    * ``PHYSICAL`` (default for most dimensions): record-by-record
      in the order produced. For text streams this is character
      equality. For files this is path-sorted byte equality.
    * ``KEY_SORTED``: both sides are sorted by a declared key
      before comparison. The key is per-dimension.
    * ``SET``: both sides are treated as sets, ignoring order.
      This is the weakest mode and should be used only when
      ordering is not a semantic concern.
    """

    PHYSICAL = "PHYSICAL"
    KEY_SORTED = "KEY_SORTED"
    SET = "SET"

    @property
    def is_strict(self) -> bool:
        """Whether the mode enforces ordering."""
        return self is ComparisonMode.PHYSICAL


# Default comparison mode per dimension. The defaults are the
# strictest modes available.
DEFAULT_COMPARISON_MODES: Final[Mapping[str, ComparisonMode]] = {
    "exit_code": ComparisonMode.PHYSICAL,
    "stdout": ComparisonMode.PHYSICAL,
    "stderr": ComparisonMode.PHYSICAL,
    "output_files": ComparisonMode.KEY_SORTED,
    "db_state": ComparisonMode.KEY_SORTED,
    "sqlcode_seq": ComparisonMode.PHYSICAL,
    "sqlstate_seq": ComparisonMode.PHYSICAL,
    "null_indicator_seq": ComparisonMode.PHYSICAL,
    "transaction_state": ComparisonMode.PHYSICAL,
    "file_status_seq": ComparisonMode.PHYSICAL,
    "cics_state": ComparisonMode.PHYSICAL,
    "batch_state": ComparisonMode.PHYSICAL,
}


@dataclass(frozen=True)
class RequiredDimensions:
    """The set of dimensions required for the comparison.

    Each dimension is identified by its canonical name (see
    ``modernize_v2.verification.observation.ALL_DIMENSIONS``).
    """

    dimensions: tuple[str, ...] = field(default_factory=tuple)
    modes: Mapping[str, ComparisonMode] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.dimensions is None:  # type: ignore[unreachable]
            object.__setattr__(self, "dimensions", ())
        if self.modes is None:  # type: ignore[unreachable]
            object.__setattr__(self, "modes", {})
        # Validate dimension names.
        for d in self.dimensions:
            if d not in ALL_DIMENSIONS:
                raise ContractValidationError(
                    f"unknown required dimension: {d!r}"
                )
        # Validate modes.
        for d, m in self.modes.items():
            if d not in ALL_DIMENSIONS:
                raise ContractValidationError(
                    f"unknown dimension in modes: {d!r}"
                )
            if not isinstance(m, ComparisonMode):
                raise ContractValidationError(
                    f"mode for {d!r} must be a ComparisonMode, got {type(m).__name__}"
                )
        # If a dimension is required, it must have a mode
        # (defaulting to PHYSICAL if not explicit).
        for d in self.dimensions:
            if d not in self.modes:
                # Mutable default is fine; we are only checking.
                pass

    def mode_for(self, dimension: str) -> ComparisonMode:
        if dimension not in self.modes:
            return DEFAULT_COMPARISON_MODES.get(
                dimension, ComparisonMode.PHYSICAL
            )
        return self.modes[dimension]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimensions": list(self.dimensions),
            "modes": {
                k: v.value for k, v in self.modes.items()
            },
        }


@dataclass(frozen=True)
class SeedDeclaration:
    """A declared seed data item.

    V2 does not auto-execute ``data/*.sql``. Every seed is
    declared explicitly. The executor (Phase 2K) accepts only
    the kinds listed in ``allowed_statement_kinds`` (default:
    ``INSERT_INTO``, ``MERGE_INTO``).
    """

    name: str
    table: str
    source_path: str
    allowed_statement_kinds: tuple[str, ...] = (
        "INSERT_INTO", "MERGE_INTO",
    )

    def __post_init__(self) -> None:
        for f in (self.name, self.table, self.source_path):
            if not isinstance(f, str) or not f:
                raise ValueError("seed fields must be non-empty strings")
        if not self.allowed_statement_kinds:
            raise ValueError(
                "seed must declare at least one allowed statement kind"
            )
        bad = set(self.allowed_statement_kinds) - {
            "INSERT_INTO", "MERGE_INTO",
        }
        if bad:
            raise ContractValidationError(
                f"unsupported seed statement kinds: {sorted(bad)}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "table": self.table,
            "source_path": self.source_path,
            "allowed_statement_kinds": list(self.allowed_statement_kinds),
        }


@dataclass(frozen=True)
class ArtifactExpectation:
    """An artifact the comparator expects to see in the observation.

    Used for output_files, db_state, batch_state, etc.
    """

    name: str
    artifact_kind: str
    present: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be a non-empty string")
        if self.artifact_kind not in (
            "file", "table", "batch_step", "cics_channel",
        ):
            raise ContractValidationError(
                f"unknown artifact_kind: {self.artifact_kind!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "artifact_kind": self.artifact_kind,
            "present": self.present,
        }


class ContractValidationError(ValueError):
    """Raised when a contract is invalid.

    The pipeline must fail-closed: a contract that does not
    validate is a hard error. The error message must be specific
    so the operator can fix the contract.
    """


@dataclass(frozen=True)
class VerificationContract:
    """An immutable verification contract.

    The contract is the single source of truth for "what
    counts as a successful comparison" for a workload. The
    comparator (Phase 2J) is a pure function of the contract and
    two observations; it does not invent comparison rules on
    the fly.
    """

    contract_id: str
    workload_id: str
    required: RequiredDimensions
    encoding: Encoding
    seeds: tuple[SeedDeclaration, ...] = field(default_factory=tuple)
    expected_artifacts: tuple[ArtifactExpectation, ...] = field(
        default_factory=tuple
    )
    policy_version: str = "2.0.0-alpha.0"
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.contract_id, str) or not self.contract_id:
            raise ValueError("contract_id must be a non-empty string")
        if not isinstance(self.workload_id, str) or not self.workload_id:
            raise ValueError("workload_id must be a non-empty string")
        if not isinstance(self.required, RequiredDimensions):
            raise TypeError("required must be a RequiredDimensions")
        if not isinstance(self.encoding, Encoding):
            raise TypeError("encoding must be an Encoding")
        if not self.required.dimensions:
            raise ContractValidationError(
                "contract must declare at least one required dimension"
            )
        # Validate seeds.
        for s in self.seeds:
            if not isinstance(s, SeedDeclaration):
                raise TypeError("seeds must be SeedDeclaration instances")
        # Validate expected artifacts.
        for a in self.expected_artifacts:
            if not isinstance(a, ArtifactExpectation):
                raise TypeError(
                    "expected_artifacts must be ArtifactExpectation instances"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "workload_id": self.workload_id,
            "required": self.required.to_dict(),
            "encoding": {
                "source_codepage": self.encoding.source_codepage,
                "java_charset": self.encoding.java_charset,
                "record_encoding": self.encoding.record_encoding,
                "numeric_encoding": self.encoding.numeric_encoding,
                "signed_encoding": self.encoding.signed_encoding,
            },
            "seeds": [s.to_dict() for s in self.seeds],
            "expected_artifacts": [a.to_dict() for a in self.expected_artifacts],
            "policy_version": self.policy_version,
            "notes": self.notes,
        }

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def content_hash(self) -> str:
        return hashlib.sha256(
            self.to_canonical_json().encode("utf-8")
        ).hexdigest()


def default_contract(
    workload_id: str,
    *,
    contract_id: str | None = None,
    required_dimensions: tuple[str, ...] | None = None,
    encoding: Encoding | None = None,
) -> VerificationContract:
    """Build a default contract for a workload.

    The default requires ``exit_code``, ``stdout``, ``stderr``,
    ``output_files``, ``db_state``, ``sqlcode_seq``,
    ``sqlstate_seq``, ``null_indicator_seq``, ``transaction_state``,
    ``file_status_seq``, ``cics_state``, and ``batch_state`` —
    every dimension that the architecture specifies in
    §24.1.

    The default encoding is UTF-8.
    """
    if required_dimensions is None:
        required_dimensions = ALL_DIMENSIONS
    if encoding is None:
        encoding = Encoding(
            source_codepage="UTF-8",
            java_charset="UTF-8",
        )
    if contract_id is None:
        contract_id = (
            f"contract:{workload_id}:v2"
        )
    return VerificationContract(
        contract_id=contract_id,
        workload_id=workload_id,
        required=RequiredDimensions(dimensions=required_dimensions),
        encoding=encoding,
    )


__all__ = [
    "ComparisonMode",
    "DEFAULT_COMPARISON_MODES",
    "RequiredDimensions",
    "SeedDeclaration",
    "ArtifactExpectation",
    "ContractValidationError",
    "VerificationContract",
    "default_contract",
]
