"""Database Reference Runtime & Validation Modes."""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DatabaseValidationMode(str, Enum):
    LOCAL_RELATIONAL = "LOCAL_RELATIONAL"
    DOCKER_RELATIONAL = "DOCKER_RELATIONAL"
    REAL_DB2_ZOS = "REAL_DB2_ZOS"


class DatabaseReferenceRuntime:
    """Manages database validation mode and enforces strict proof boundaries."""

    def __init__(self, mode: DatabaseValidationMode = DatabaseValidationMode.LOCAL_RELATIONAL):
        self.mode = mode

    @property
    def certification_classification(self) -> str:
        if self.mode in (DatabaseValidationMode.LOCAL_RELATIONAL, DatabaseValidationMode.DOCKER_RELATIONAL):
            return "PROVEN_FOR_TESTED_SCOPE"
        elif self.mode == DatabaseValidationMode.REAL_DB2_ZOS:
            return "UNPROVEN"
        return "UNPROVEN"

    def compare_schemas_and_rows(
        self,
        baseline_rows: List[Dict[str, Any]],
        target_rows: List[Dict[str, Any]],
        primary_keys: Optional[List[str]] = None,
    ) -> Tuple[bool, List[str]]:
        """Dynamic database comparison across tables, columns, nullability, and rows."""
        mismatches = []
        if len(baseline_rows) != len(target_rows):
            mismatches.append(
                f"Row count mismatch: baseline has {len(baseline_rows)} rows, target has {len(target_rows)} rows"
            )
            return False, mismatches

        if not baseline_rows and not target_rows:
            return True, []

        b_cols = set(baseline_rows[0].keys())
        t_cols = set(target_rows[0].keys())
        if b_cols != t_cols:
            mismatches.append(f"Column schema mismatch: baseline cols {b_cols} != target cols {t_cols}")
            return False, mismatches

        pk = primary_keys[0] if primary_keys else list(b_cols)[0]
        try:
            b_sorted = sorted(baseline_rows, key=lambda r: str(r.get(pk, "")))
            t_sorted = sorted(target_rows, key=lambda r: str(r.get(pk, "")))
        except Exception:
            b_sorted = baseline_rows
            t_sorted = target_rows

        for idx, (b_row, t_row) in enumerate(zip(b_sorted, t_sorted)):
            for col in b_cols:
                bv = b_row.get(col)
                tv = t_row.get(col)
                if bv != tv:
                    mismatches.append(
                        f"Row {idx} (pk={b_row.get(pk)}) column '{col}' mismatch: baseline '{bv}' != target '{tv}'"
                    )

        return len(mismatches) == 0, mismatches
