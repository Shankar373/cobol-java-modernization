"""Machine-readable COBOL/Mainframe Capability Matrix.

Defines the verification status, detection mechanisms, and implementation state
of all key pipeline features.
"""

from typing import Dict, Any, List

class CapabilityStatus:
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"

# The master dictionary containing capability specs.
CAPABILITIES: Dict[str, Dict[str, Any]] = {
    # COBOL statements & constructs
    "COBOL.IF": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "IF/ELSE statement parser",
        "evidence": "tests/test_phase8_control_flow.py",
        "limitations": "None",
    },
    "COBOL.EVALUATE": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EVALUATE statement parser",
        "evidence": "tests/test_native_evaluate.py",
        "limitations": "None",
    },
    "COBOL.PERFORM": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "PERFORM loops parser",
        "evidence": "tests/test_native_perform_varying.py",
        "limitations": "None",
    },
    "COBOL.PERFORM_THRU": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "PERFORM THRU block boundaries constructor",
        "evidence": "tests/test_native_paragraph_control.py",
        "limitations": "None",
    },
    "COBOL.CALL_STATIC": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "CALL literal pattern extraction",
        "evidence": "tests/test_native_call_translation.py",
        "limitations": "None",
    },
    "COBOL.CALL_DYNAMIC": {
        "status": CapabilityStatus.REVIEW_REQUIRED,
        "detection": "CALL identifier variable extraction",
        "evidence": "tests/test_dependencies.py",
        "limitations": "Requires static program registry lookup.",
    },
    "COBOL.COMP": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "USAGE BINARY/COMP mapping",
        "evidence": "tests/test_native_type_mapping.py",
        "limitations": "None",
    },
    "COBOL.COMP_3": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "USAGE PACKED-DECIMAL/COMP-3 mapping",
        "evidence": "tests/test_phase8_arithmetic_errors.py",
        "limitations": "None",
    },
    "COBOL.REDEFINES": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "REDEFINES overlap mapping",
        "evidence": "tests/test_phase8_redefines.py",
        "limitations": "None",
    },
    "COBOL.OCCURS": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "OCCURS subscripting mapping",
        "evidence": "tests/test_native_occurs.py",
        "limitations": "None",
    },
    "COBOL.COPY": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "COPY book preprocessor",
        "evidence": "tests/test_lexer.py",
        "limitations": "None",
    },
    # File I/O
    "FILE.SEQUENTIAL": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "SEQUENTIAL organization mapping",
        "evidence": "tests/test_phase8_file_semantics.py",
        "limitations": "None",
    },
    "FILE.VSAM_KSDS": {
        "status": CapabilityStatus.PARTIAL,
        "detection": "INDEXED access mode mapping",
        "evidence": "tests/test_phase8_file_semantics.py",
        "limitations": "Mapped to SQL databases in target Track B.",
    },
    # SQL operations
    "SQL.DB2.SELECT": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL SELECT parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    "SQL.DB2.INSERT": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL INSERT parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    "SQL.DB2.UPDATE": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL UPDATE parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    "SQL.DB2.DELETE": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL DELETE parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    "SQL.DB2.CURSOR": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL DECLARE/OPEN/FETCH/CLOSE CURSOR parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    "SQL.DB2.TRANSACTION": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL COMMIT/ROLLBACK parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    "SQL.DB2.HOST_VARIABLE": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "EXEC SQL host variable reference parser",
        "evidence": "tests/test_db2_acceptance.py",
        "limitations": "None",
    },
    # JCL & CICS
    "JCL.JOB": {
        "status": CapabilityStatus.PARTIAL,
        "detection": "JCL JOB card parsing",
        "evidence": "tests/test_jcl_modernization.py",
        "limitations": "Basic JCL parameters mapped to Spring Batch context.",
    },
    "JCL.EXEC": {
        "status": CapabilityStatus.PARTIAL,
        "detection": "JCL EXEC card parsing",
        "evidence": "tests/test_jcl_modernization.py",
        "limitations": "Basic step transitions and conditional bypass routing.",
    },
    "JCL.DD": {
        "status": CapabilityStatus.PARTIAL,
        "detection": "JCL DD card parsing",
        "evidence": "tests/test_jcl_modernization.py",
        "limitations": "Binds JCL symbols and inputs dynamically.",
    },
    # Backward compatible string keys
    "MOVE": {"status": CapabilityStatus.SUPPORTED},
    "COMPUTE": {"status": CapabilityStatus.SUPPORTED},
    "ADD": {"status": CapabilityStatus.SUPPORTED},
    "SUBTRACT": {"status": CapabilityStatus.SUPPORTED},
    "MULTIPLY": {"status": CapabilityStatus.SUPPORTED},
    "DIVIDE": {"status": CapabilityStatus.SUPPORTED},
    "COMP": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "USAGE BINARY/COMP mapping",
        "limitations": "None",
    },
    "COMP-3": {
        "status": CapabilityStatus.SUPPORTED,
        "detection": "USAGE PACKED-DECIMAL/COMP-3 mapping",
        "limitations": "None",
    },
    "IF": {"status": CapabilityStatus.SUPPORTED},
    "EVALUATE": {"status": CapabilityStatus.SUPPORTED},
    "PERFORM": {"status": CapabilityStatus.SUPPORTED},
    "PERFORM_THRU": {"status": CapabilityStatus.SUPPORTED},
    "static_CALL": {"status": CapabilityStatus.SUPPORTED},
    "dynamic_CALL": {
        "status": CapabilityStatus.PARTIAL,
        "detection": "CALL identifier variable extraction",
        "evidence": "tests/test_dependencies.py",
        "limitations": "Requires static program registry lookup.",
    },
    "EXEC_SQL": {"status": CapabilityStatus.PARTIAL},
    "EXEC_CICS": {"status": CapabilityStatus.REVIEW_REQUIRED},
    "JCL": {"status": CapabilityStatus.PARTIAL},
    # Unsupported mainframe extensions
    "IMS_MQ": {"status": CapabilityStatus.UNSUPPORTED},
    "IMS_DB": {"status": CapabilityStatus.UNSUPPORTED},
    "MQ_SERIES": {"status": CapabilityStatus.UNSUPPORTED},
}

def classify_feature(name: str) -> str:
    """Return status classification for a feature name."""
    spec = CAPABILITIES.get(name) or CAPABILITIES.get(name.upper())
    if not spec:
        # Check CICS and BMS wildcard matches
        if name.upper().startswith("CICS."):
            return CapabilityStatus.REVIEW_REQUIRED
        if name.upper().startswith("BMS."):
            return CapabilityStatus.REVIEW_REQUIRED
        return CapabilityStatus.UNKNOWN
    return spec["status"]

def get_unsupported_features(features: List[str]) -> List[str]:
    """Filter list of detected features for unsupported/unknown items."""
    unsupported = []
    for f in features:
        if classify_feature(f) in (CapabilityStatus.UNSUPPORTED, CapabilityStatus.UNKNOWN):
            unsupported.append(f)
    return unsupported
