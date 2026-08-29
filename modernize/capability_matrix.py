"""Machine-readable COBOL/Mainframe Capability Matrix.

Evidence taxonomy (from most to least verified):
  UNSUPPORTED            — no detection, no parsing, no generation
  PARSED_ONLY            — parsed into IR but no Java generated (or generation is stub/comment-only)
  GENERATED_ONLY         — Java generated but never executed in a differential test
  UNIT_TESTED            — unit-tested in isolation (Java compile + run) without GnuCOBOL comparison
  DIFFERENTIALLY_VERIFIED — GnuCOBOL and Java both ran, relevant outputs compared, reproducible in CI
  PRODUCTION_QUALIFIED   — reserved; not claimed for any feature yet
"""

from typing import Dict, Any, List

class EvidenceLevel:
    UNSUPPORTED             = "UNSUPPORTED"
    PARSED_ONLY             = "PARSED_ONLY"
    GENERATED_ONLY          = "GENERATED_ONLY"
    UNIT_TESTED             = "UNIT_TESTED"
    DIFFERENTIALLY_VERIFIED = "DIFFERENTIALLY_VERIFIED"
    PRODUCTION_QUALIFIED    = "PRODUCTION_QUALIFIED"  # reserved

# Legacy shim so any code importing old constants still compiles.
class CapabilityStatus:
    SUPPORTED        = EvidenceLevel.UNIT_TESTED       # conservative downgrade
    PARTIAL          = EvidenceLevel.GENERATED_ONLY
    REVIEW_REQUIRED  = EvidenceLevel.PARSED_ONLY
    UNSUPPORTED      = EvidenceLevel.UNSUPPORTED
    UNKNOWN          = EvidenceLevel.UNSUPPORTED


def _e(
    evidence_level: str,
    *,
    parser_function: str = None,
    generator_function: str = None,
    runtime_helper: str = None,
    existing_tests: List[str] = None,
    known_limitations: List[str] = None,
    unsupported_patterns: List[str] = None,
    recommended_next_test: str = None,
    notes: str = "",
) -> Dict[str, Any]:
    return {
        "evidence_level": evidence_level,
        "parser_function": parser_function,
        "generator_function": generator_function,
        "runtime_helper": runtime_helper,
        "existing_tests": existing_tests or [],
        "known_limitations": known_limitations or [],
        "unsupported_patterns": unsupported_patterns or [],
        "recommended_next_test": recommended_next_test,
        "notes": notes,
        # Legacy field kept for backward compatibility
        "status": evidence_level,
    }


CAPABILITIES: Dict[str, Dict[str, Any]] = {

    # =========================================================
    # PIC / USAGE
    # =========================================================
    "PIC.DISPLAY_NUMERIC": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolNumeric / CobolNumericSpec",
        existing_tests=[
            "tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_pic9_integer_arithmetic_baseline]",
            "tests/test_native_type_mapping.py",
        ],
        known_limitations=["USAGE IS INDEX not supported"],
        recommended_next_test="Verify PIC 9(18) boundary near long overflow",
    ),
    "PIC.DISPLAY_ALPHA": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="String / CobolFormatHelper",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_a_basic_move"],
        known_limitations=["PIC A not separately tested from PIC X"],
        recommended_next_test="Add PIC A differential fixture",
    ),
    "PIC.EDITED_NUMERIC": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolFormatHelper",
        existing_tests=["tests/test_phase8_pic_formatting.py"],
        known_limitations=["CR/DB suffix editing not fully tested"],
        unsupported_patterns=["PIC +(5)9 float-style editing"],
        recommended_next_test="Differential fixture for PIC ZZ,ZZZ.99CR",
    ),
    "PIC.EDITED_ALPHA": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolFormatHelper",
        existing_tests=["tests/test_phase8_pic_formatting.py"],
        known_limitations=[],
        recommended_next_test="Differential fixture for PIC X(5)/X(5)",
    ),
    "USAGE.DISPLAY": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolNumeric (DISPLAY path)",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[*]"],
        known_limitations=[],
    ),
    "USAGE.COMP": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolNumeric (COMP path via CobolUsage.COMP)",
        existing_tests=["tests/test_native_type_mapping.py"],
        known_limitations=["COMP-1 (float) and COMP-2 (double) not supported"],
        unsupported_patterns=["USAGE COMP-1", "USAGE COMP-2"],
        recommended_next_test="Differential COMP arithmetic fixture",
    ),
    "USAGE.COMP_3": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolNumeric (COMP-3 BCD encode/decode)",
        existing_tests=[
            "tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_comp3_roundtrip]",
            "tests/test_phase8_arithmetic_errors.py",
        ],
        known_limitations=["Negative zero not separately tested"],
        recommended_next_test="Differential file write+read with COMP-3 field",
    ),
    "USAGE.COMP_5": _e(
        EvidenceLevel.GENERATED_ONLY,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_field_decl",
        runtime_helper="CobolNumeric (mapped to CobolUsage.COMP)",
        existing_tests=[],
        known_limitations=["COMP-5 native-endian binary not verified differentially"],
        recommended_next_test="Differential COMP-5 boundary value fixture",
    ),
    "USAGE.INDEX": _e(
        EvidenceLevel.UNSUPPORTED,
        known_limitations=["USAGE IS INDEX not parsed as a distinct numeric type"],
        unsupported_patterns=["USAGE IS INDEX"],
        recommended_next_test="Add INDEX support diagnostic",
    ),

    # =========================================================
    # ARITHMETIC
    # =========================================================
    "ARITH.ADD": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_arithmetic_stmt",
        generator_function="NativeProgramGenerator._emit_add",
        runtime_helper="CobolArithmetic.add / CobolNumeric.assign",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_pic9_integer_arithmetic_baseline]"],
        known_limitations=["ADD CORRESPONDING not supported"],
        unsupported_patterns=["ADD CORRESPONDING"],
        recommended_next_test="ADD multi-receiver differential",
    ),
    "ARITH.SUBTRACT": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_arithmetic_stmt",
        generator_function="NativeProgramGenerator._emit_subtract",
        runtime_helper="CobolArithmetic.subtract / CobolNumeric.assign",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_negative_subtract]"],
        known_limitations=["SUBTRACT CORRESPONDING not supported"],
        unsupported_patterns=["SUBTRACT CORRESPONDING"],
    ),
    "ARITH.MULTIPLY": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_arithmetic_stmt",
        generator_function="NativeProgramGenerator._emit_multiply",
        runtime_helper="CobolArithmetic.multiply / CobolNumeric.assign",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_pics9_signed_arithmetic]"],
        known_limitations=["MULTIPLY CORRESPONDING not supported"],
        unsupported_patterns=["MULTIPLY CORRESPONDING"],
    ),
    "ARITH.DIVIDE": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_arithmetic_stmt",
        generator_function="NativeProgramGenerator._emit_divide",
        runtime_helper="CobolArithmetic.divide (MathContext.DECIMAL128)",
        existing_tests=[
            "tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_division_scale_normalization]",
            "tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_divide_remainder]",
        ],
        known_limitations=["Recurring decimal truncated to target PIC scale"],
        recommended_next_test="Differential 1/3 with PIC V99 vs V9(9)",
    ),
    "ARITH.COMPUTE": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_compute_stmt",
        generator_function="NativeProgramGenerator._emit_compute",
        runtime_helper="CobolArithmetic (all ops)",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_compute_mixed]"],
        known_limitations=["Fractional exponents are unsupported and fail-fast with a clear diagnostic (no double math)"],
        unsupported_patterns=["Non-integer COMPUTE ** exponent"],
        recommended_next_test="Verify runtime exception on non-integer exponent",
    ),
    "ARITH.ROUNDED": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_arithmetic_stmt",
        generator_function="NativeProgramGenerator._emit_rounded_assign",
        runtime_helper="CobolRoundingMode.NEAREST_AWAY_FROM_ZERO",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_rounded_arithmetic]"],
        known_limitations=["Only NEAREST_AWAY_FROM_ZERO (HALF_UP) is emitted for plain ROUNDED"],
        unsupported_patterns=["ROUNDED MODE IS NEAREST-EVEN", "ROUNDED MODE IS TOWARD-GREATER"],
        recommended_next_test="Differential negative halfway rounding",
    ),
    "ARITH.ON_SIZE_ERROR": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_arithmetic_stmt",
        generator_function="NativeProgramGenerator._emit_size_error_guard",
        runtime_helper="SizeErrorPolicy.CHECKED / CobolNumeric.assign",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_positive_target_field_overflow]"],
        known_limitations=["NOT ON SIZE ERROR clause generated but coverage limited"],
        recommended_next_test="Differential NOT ON SIZE ERROR path",
    ),

    # =========================================================
    # MOVE
    # =========================================================
    "MOVE.ALPHA_TO_ALPHA": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_move_stmt",
        generator_function="NativeProgramGenerator._emit_move",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_a_basic_move"],
        known_limitations=["Truncation on right, no padding verified differentially for PIC X(N) → PIC X(M) with N>M"],
    ),
    "MOVE.NUMERIC_TO_NUMERIC": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_move_stmt",
        generator_function="NativeProgramGenerator._emit_move",
        runtime_helper="CobolNumeric.assign",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_b_parity[milestone_b_pic9v99_implied_decimal_assignment]"],
        known_limitations=["MOVE CORRESPONDING not supported"],
        unsupported_patterns=["MOVE CORRESPONDING"],
    ),
    "MOVE.GROUP_TO_GROUP": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_move_stmt",
        generator_function="NativeProgramGenerator._emit_move",
        existing_tests=["tests/test_phase8_layout_integration.py"],
        known_limitations=["Group MOVE treated as byte copy; byte-exact differential not verified"],
        recommended_next_test="Differential group MOVE byte-comparison fixture",
    ),

    # =========================================================
    # REDEFINES / OCCURS
    # =========================================================
    "REDEFINES.SCALAR": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_redefines",
        existing_tests=["tests/test_phase8_redefines.py"],
        known_limitations=["Shared byte-backed storage not used; overlapping views via copy-on-access"],
        recommended_next_test="Differential write-through scalar REDEFINES fixture",
    ),
    "REDEFINES.GROUP": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_redefines",
        existing_tests=["tests/test_phase8_redefines.py"],
        known_limitations=["Group REDEFINES byte-exact write-through not differentially verified"],
        recommended_next_test="Differential group REDEFINES fixture (write via one view, read via other)",
    ),
    "REDEFINES.COMP3_VIEW": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_redefines",
        runtime_helper="CobolNumeric (COMP-3 encode)",
        existing_tests=["tests/test_phase8_redefines.py"],
        known_limitations=["Raw bytes not compared differentially"],
        recommended_next_test="Differential COMP-3 byte view fixture",
    ),
    "REDEFINES.NESTED_COMPLEX": _e(
        EvidenceLevel.PARSED_ONLY,
        known_limitations=["Nested REDEFINES with OCCURS not fully generated"],
        unsupported_patterns=["REDEFINES of OCCURS-containing group", "3+ level nested REDEFINES"],
        recommended_next_test="Add diagnostic for unsupported nested REDEFINES",
    ),
    "OCCURS.FIXED": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_occurs",
        existing_tests=["tests/test_native_occurs.py"],
        known_limitations=["OCCURS inside REDEFINES not differentially verified"],
        recommended_next_test="Differential OCCURS table read/write fixture",
    ),
    "OCCURS.DEPENDING_ON": _e(
        EvidenceLevel.GENERATED_ONLY,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_occurs_depending",
        existing_tests=[],
        known_limitations=["OCCURS DEPENDING ON generated but runtime bounds not differentially verified"],
        recommended_next_test="Differential ODO fixture with varying bound",
    ),

    # =========================================================
    # PROCEDURE DIVISION / CONTROL FLOW
    # =========================================================
    "PROC.PERFORM": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_perform_stmt",
        generator_function="NativeProgramGenerator._emit_perform",
        existing_tests=["tests/test_native_perform_varying.py", "tests/test_phase8_control_flow.py"],
        recommended_next_test="Differential PERFORM VARYING fixture",
    ),
    "PROC.PERFORM_THRU": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_perform_stmt",
        generator_function="NativeProgramGenerator._emit_perform_thru",
        existing_tests=["tests/test_native_paragraph_control.py"],
        known_limitations=["EXIT PARAGRAPH inside THRU range not differentially verified"],
        recommended_next_test="Differential PERFORM THRU fixture with paragraph range",
    ),
    "PROC.PERFORM_VARYING": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_perform_stmt",
        generator_function="NativeProgramGenerator._emit_perform",
        existing_tests=["tests/test_native_perform_varying.py"],
        recommended_next_test="Differential PERFORM VARYING with AFTER clause",
    ),
    "PROC.GO_TO": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_goto_stmt",
        generator_function="NativeProgramGenerator._emit_goto",
        existing_tests=["tests/test_phase8_control_flow.py"],
        known_limitations=["GO TO inside PERFORM THRU range not differentially verified"],
        unsupported_patterns=["GO TO DEPENDING ON"],
        recommended_next_test="Differential GO TO within performed paragraph range",
    ),
    "PROC.CALL_STATIC": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_call_stmt",
        generator_function="NativeProgramGenerator._emit_call",
        existing_tests=["tests/test_native_call_translation.py"],
        known_limitations=["BY VALUE not differentially verified", "BY CONTENT isolation not differentially verified"],
        recommended_next_test="Differential CALL BY REFERENCE mutation fixture",
    ),
    "PROC.CALL_DYNAMIC": _e(
        EvidenceLevel.GENERATED_ONLY,
        parser_function="CobolParser._parse_call_stmt",
        generator_function="NativeProgramGenerator._emit_call",
        existing_tests=["tests/test_dependencies.py"],
        known_limitations=["Dynamic CALL target resolved via program registry; unknown targets produce diagnostic"],
        unsupported_patterns=["CALL USING identifier resolved at runtime with no registry entry"],
        recommended_next_test="Differential dynamic CALL fixture",
    ),
    "PROC.CALL_BY_REFERENCE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_call_stmt",
        generator_function="NativeProgramGenerator._emit_call",
        existing_tests=["tests/test_native_call_translation.py"],
        known_limitations=["Caller-visible mutation not differentially verified"],
        recommended_next_test="Differential BY REFERENCE mutation test",
    ),
    "PROC.CALL_BY_CONTENT": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_call_stmt",
        generator_function="NativeProgramGenerator._emit_call",
        existing_tests=["tests/test_native_call_translation.py"],
        known_limitations=["Caller isolation not differentially verified"],
        recommended_next_test="Differential BY CONTENT isolation test",
    ),
    "PROC.GOBACK": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_goback_stmt",
        generator_function="NativeProgramGenerator._emit_goback",
        existing_tests=["tests/test_phase8_control_flow.py"],
    ),
    "PROC.STOP_RUN": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_stop_stmt",
        generator_function="NativeProgramGenerator._emit_stop_run",
        existing_tests=["tests/test_phase8_control_flow.py"],
    ),
    "PROC.EVALUATE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_evaluate_stmt",
        generator_function="NativeProgramGenerator._emit_evaluate",
        existing_tests=["tests/test_native_evaluate.py"],
        known_limitations=["EVALUATE TRUE ALSO TRUE (multi-subject) not differentially verified"],
        recommended_next_test="Differential EVALUATE with WHEN OTHER",
    ),
    "PROC.IF": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_if_stmt",
        generator_function="NativeProgramGenerator._emit_if",
        existing_tests=["tests/test_phase8_control_flow.py"],
    ),
    "PROC.SECTIONS": _e(
        EvidenceLevel.GENERATED_ONLY,
        parser_function="CobolParser._parse_section",
        generator_function="NativeProgramGenerator._emit_section",
        existing_tests=[],
        known_limitations=["Sections with PERFORM THRU not differentially verified"],
        recommended_next_test="Differential SECTION fall-through fixture",
    ),

    # =========================================================
    # STRING / INSPECT / UNSTRING
    # =========================================================
    "STRING.STRING_STMT": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_string_stmt",
        generator_function="NativeProgramGenerator._emit_string",
        existing_tests=["tests/test_phase8_string_operations.py"],
        recommended_next_test="Differential STRING INTO with POINTER",
    ),
    "STRING.UNSTRING_STMT": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_unstring_stmt",
        generator_function="NativeProgramGenerator._emit_unstring",
        existing_tests=["tests/test_phase8_string_operations.py"],
    ),
    "STRING.INSPECT": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_inspect_stmt",
        generator_function="NativeProgramGenerator._emit_inspect",
        existing_tests=["tests/test_phase8_string_operations.py"],
    ),

    # =========================================================
    # FILE I/O
    # =========================================================
    "FILE.LINE_SEQUENTIAL": _e(
        EvidenceLevel.DIFFERENTIALLY_VERIFIED,
        parser_function="CobolParser._parse_file_control",
        generator_function="NativeProgramGenerator._emit_file_io",
        existing_tests=["tests/test_parity_fixtures.py::test_milestone_a_line_sequential_file"],
        known_limitations=["EBCDIC encoding not tested", "Variable-length records not supported"],
        recommended_next_test="Differential trailing-space preservation fixture",
    ),
    "FILE.SEQUENTIAL_FIXED": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_file_control",
        generator_function="NativeProgramGenerator._emit_file_io",
        existing_tests=[
            "tests/test_parity_fixtures.py::test_milestone_b_fixed_binary_file_io",
            "tests/test_phase8_file_semantics.py",
        ],
        known_limitations=["Record boundary not enforced by read length; uses newline-delimited internally"],
        recommended_next_test="Differential fixed-length record boundary verification",
    ),
    "FILE.SEQUENTIAL_EBCDIC": _e(
        EvidenceLevel.UNSUPPORTED,
        known_limitations=["No EBCDIC charset codec in file I/O path"],
        unsupported_patterns=["CODEPAGE EBCDIC", "IBM-1047 encoding"],
        recommended_next_test="Add EBCDIC file codec and differential fixture",
    ),
    "FILE.RELATIVE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_file_control",
        generator_function="NativeProgramGenerator._emit_file_io",
        existing_tests=["tests/test_vsam_rrds.py"],
        known_limitations=["Numeric RRN stored as string key internally"],
        recommended_next_test="Differential relative-file random access fixture",
    ),
    "FILE.INDEXED_KSDS": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_file_control",
        generator_function="NativeProgramGenerator._emit_file_io",
        runtime_helper="VsamIndexedStore",
        existing_tests=["tests/test_vsam_ksds_stage2.py"],
        known_limitations=["Alternate indexes partial only", "Duplicate key behavior differentially verified via test_vsam_ksds_stage2"],
        recommended_next_test="Differential indexed file START + READ NEXT fixture",
    ),
    "FILE.FILE_STATUS": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_file_control",
        generator_function="NativeProgramGenerator._emit_file_io",
        existing_tests=["tests/test_native_file_io.py", "tests/test_phase8_file_semantics.py"],
        known_limitations=["FILE STATUS not captured in parity harness ExecutionResult"],
        recommended_next_test="Add FILE STATUS capture to parity harness; differential fixture",
    ),
    "FILE.VARIABLE_LENGTH": _e(
        EvidenceLevel.UNSUPPORTED,
        known_limitations=["RDW/variable-block not supported"],
        unsupported_patterns=["RECORDING MODE V", "RECORDING MODE U"],
        recommended_next_test="Add diagnostic COBOL_UNSUPPORTED_RECORD_FORMAT",
    ),

    # =========================================================
    # EMBEDDED SQL (DB2)
    # =========================================================
    "SQL.SELECT_INTO": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_acceptance.py", "tests/test_db2_stage1.py"],
        known_limitations=["Not differentially verified via GnuCOBOL (blocked at baseline)"],
        recommended_next_test="Differential SQL fixture using H2 vs GnuCOBOL baseline bypass",
    ),
    "SQL.INSERT": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_acceptance.py"],
        known_limitations=["Not differentially verified vs GnuCOBOL"],
    ),
    "SQL.UPDATE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_acceptance.py"],
    ),
    "SQL.DELETE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_acceptance.py"],
    ),
    "SQL.CURSOR": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_acceptance.py"],
        known_limitations=["Cursor paging not differentially verified"],
    ),
    "SQL.NULL_INDICATORS": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_dialect_null_indicators.py"],
    ),
    "SQL.COMMIT_ROLLBACK": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_stage1.py"],
        known_limitations=["Transaction boundary behavior not differentially verified"],
        recommended_next_test="Differential commit/rollback visibility test",
    ),
    "SQL.SQLCODE_SQLSTATE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_error_mapper.py"],
        known_limitations=["SQLCODE values not captured in parity harness ExecutionResult"],
    ),
    "SQL.HOST_VARIABLES": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_exec_sql",
        generator_function="NativeProgramGenerator._emit_exec_sql",
        existing_tests=["tests/test_db2_acceptance.py"],
    ),

    # =========================================================
    # EXEC CICS
    # =========================================================
    "CICS.SEND_MAP": _e(
        EvidenceLevel.PARSED_ONLY,
        parser_function="CobolParser._parse_exec_cics",
        generator_function="NativeProgramGenerator._emit_exec_cics (stub)",
        existing_tests=["tests/test_cics_modernization.py"],
        known_limitations=["Stubbed; no BMS map semantics generated"],
        unsupported_patterns=["EXEC CICS SEND MAP MAPONLY ERASEAUP"],
        recommended_next_test="Add CICS command support matrix test",
    ),
    "CICS.RECEIVE_MAP": _e(
        EvidenceLevel.PARSED_ONLY,
        parser_function="CobolParser._parse_exec_cics",
        generator_function="NativeProgramGenerator._emit_exec_cics (stub)",
        existing_tests=["tests/test_cics_modernization.py"],
        known_limitations=["Stubbed only"],
    ),
    "CICS.LINK": _e(
        EvidenceLevel.PARSED_ONLY,
        parser_function="CobolParser._parse_exec_cics",
        generator_function="NativeProgramGenerator._emit_exec_cics (stub)",
        existing_tests=["tests/test_cics_modernization.py"],
    ),
    "CICS.RETURN": _e(
        EvidenceLevel.PARSED_ONLY,
        parser_function="CobolParser._parse_exec_cics",
        generator_function="NativeProgramGenerator._emit_exec_cics (stub)",
        existing_tests=["tests/test_cics_modernization.py"],
    ),
    "CICS.RESP_RESP2": _e(
        EvidenceLevel.PARSED_ONLY,
        parser_function="CobolParser._parse_exec_cics",
        generator_function="NativeProgramGenerator._emit_exec_cics (stub)",
        existing_tests=["tests/test_cics_map_semantics.py"],
        known_limitations=["RESP/RESP2 fields set to 0 by stub; not behaviorally verified"],
        recommended_next_test="CICS command support matrix with RESP routing",
    ),
    "CICS.UNSUPPORTED_COMMANDS": _e(
        EvidenceLevel.PARSED_ONLY,
        known_limitations=["All non-SEND/RECEIVE/LINK/RETURN commands stubbed with diagnostic comment"],
        unsupported_patterns=[
            "EXEC CICS READ", "EXEC CICS WRITE", "EXEC CICS REWRITE",
            "EXEC CICS DELETE", "EXEC CICS STARTBR", "EXEC CICS READNEXT",
            "EXEC CICS ENDBR", "EXEC CICS GETMAIN", "EXEC CICS FREEMAIN",
            "EXEC CICS ENQ", "EXEC CICS DEQ", "EXEC CICS SYNCPOINT",
        ],
        recommended_next_test="Add COBOL_UNSUPPORTED_CICS_COMMAND diagnostic test",
    ),

    # =========================================================
    # JCL
    # =========================================================
    "JCL.JOB_CARD": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="JclParser._parse_job_card",
        generator_function="JclGenerator._emit_job",
        existing_tests=["tests/test_jcl_modernization.py"],
        known_limitations=["JOB card parameters not fully mapped"],
    ),
    "JCL.EXEC_PGM": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="JclParser._parse_exec_card",
        generator_function="JclGenerator._emit_exec",
        existing_tests=["tests/test_jcl_modernization.py"],
        known_limitations=["COND parameter routing partial"],
    ),
    "JCL.DD_STATEMENT": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="JclParser._parse_dd_card",
        generator_function="JclGenerator._emit_dd",
        existing_tests=["tests/test_jcl_modernization.py"],
        known_limitations=["Dataset disposition (DISP=SHR/NEW/OLD) not modeled"],
        unsupported_patterns=["DISP=MOD", "UNIT=TAPE", "SPACE=(CYL,(n,m))"],
    ),
    "JCL.COND_PARAMETER": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="JclParser._parse_cond",
        generator_function="JclGenerator._emit_cond",
        existing_tests=["tests/test_jcl_symbols_complete.py"],
        known_limitations=["COND=ONLY and COND=EVEN not separately verified"],
        unsupported_patterns=["COND=ONLY", "COND=EVEN"],
        recommended_next_test="Differential JCL COND conditional bypass fixture",
    ),
    "JCL.IF_THEN_ELSE": _e(
        EvidenceLevel.GENERATED_ONLY,
        parser_function="JclParser._parse_if_stmt",
        generator_function="JclGenerator._emit_if",
        existing_tests=[],
        known_limitations=["IF/THEN/ELSE block routing generated but not differentially verified"],
        recommended_next_test="Differential JCL IF/THEN/ELSE step routing fixture",
    ),
    "JCL.SYMBOLS": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="JclParser._parse_symbols",
        generator_function="JclGenerator._emit_symbols",
        existing_tests=["tests/test_jcl_symbols_complete.py"],
    ),

    # =========================================================
    # UNSUPPORTED AREAS
    # =========================================================
    "IMS.DLI": _e(
        EvidenceLevel.UNSUPPORTED,
        known_limitations=["EXEC DLI blocked at baseline; stubbed in transpile preprocessing"],
        unsupported_patterns=["EXEC DLI CALL 'CBLTDLI'", "CALL 'AIBTDLI'", "CALL 'DFSRRC00'"],
        recommended_next_test="Add COBOL_UNSUPPORTED_IMS_CALL diagnostic test",
    ),
    "MQ.SERIES": _e(
        EvidenceLevel.UNSUPPORTED,
        known_limitations=["IBM MQ copybooks not bundled; compilation fails at baseline"],
        unsupported_patterns=["CALL 'MQPUT'", "CALL 'MQGET'", "COPY CMQV", "COPY CMQODV"],
        recommended_next_test="Add COBOL_UNSUPPORTED_MQ_CALL diagnostic and mock MQ copybooks",
    ),
    "REPORT_WRITER": _e(
        EvidenceLevel.PARSED_ONLY,
        parser_function="CobolParser._parse_report_section",
        known_limitations=["Report Writer section parsed but not generated"],
        unsupported_patterns=["INITIATE", "GENERATE", "TERMINATE"],
        recommended_next_test="Add COBOL_UNSUPPORTED_REPORT_WRITER diagnostic",
    ),
    "SORT_MERGE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_sort_stmt",
        generator_function="NativeProgramGenerator._emit_sort",
        existing_tests=["tests/test_phase8_sort_merge.py"],
        known_limitations=["SORT with USING/GIVING file only; SORT with INPUT PROCEDURE not fully verified"],
        recommended_next_test="Differential SORT with INPUT/OUTPUT PROCEDURE fixture",
    ),
    "POINTER_FIELDS": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_data_item",
        generator_function="NativeProgramGenerator._emit_pointer",
        existing_tests=["tests/test_phase8_pointers.py"],
        known_limitations=["SET ADDRESS OF not differentially verified"],
        unsupported_patterns=["SET ADDRESS OF linkage item"],
    ),
    "NEXT_SENTENCE": _e(
        EvidenceLevel.UNIT_TESTED,
        parser_function="CobolParser._parse_next_sentence",
        generator_function="NativeProgramGenerator._emit_next_sentence",
        existing_tests=["tests/test_phase8_next_sentence.py"],
    ),
}

# -----------------------------------------------------------------------
# Convenience functions (backward-compatible API surface)
# -----------------------------------------------------------------------

_LEGACY_SHIMS = {
    "MOVE": EvidenceLevel.UNIT_TESTED,
    "COMPUTE": EvidenceLevel.UNIT_TESTED,
    "ADD": EvidenceLevel.UNIT_TESTED,
    "SUBTRACT": EvidenceLevel.UNIT_TESTED,
    "MULTIPLY": EvidenceLevel.UNIT_TESTED,
    "DIVIDE": EvidenceLevel.UNIT_TESTED,
    "COMP": EvidenceLevel.UNIT_TESTED,
    "COMP-3": EvidenceLevel.UNIT_TESTED,
    "IF": EvidenceLevel.UNIT_TESTED,
    "EVALUATE": EvidenceLevel.UNIT_TESTED,
    "PERFORM": EvidenceLevel.UNIT_TESTED,
    "PERFORM_THRU": EvidenceLevel.UNIT_TESTED,
    "STATIC_CALL": EvidenceLevel.UNIT_TESTED,
    "DYNAMIC_CALL": EvidenceLevel.GENERATED_ONLY,
    "EXEC_SQL": EvidenceLevel.GENERATED_ONLY,
    "EXEC_CICS": EvidenceLevel.PARSED_ONLY,
    "JCL": EvidenceLevel.GENERATED_ONLY,
    "IMS_MQ": EvidenceLevel.UNSUPPORTED,
    "IMS_DB": EvidenceLevel.UNSUPPORTED,
    "MQ_SERIES": EvidenceLevel.UNSUPPORTED,
}


def classify_feature(name: str) -> str:
    """Return evidence_level for a feature name (backward-compatible)."""
    name_upper = name.upper()
    spec = CAPABILITIES.get(name) or CAPABILITIES.get(name_upper)
    if spec:
        return spec["evidence_level"]
    if name_upper in _LEGACY_SHIMS:
        return _LEGACY_SHIMS[name_upper]
    if name_upper.startswith("CICS."):
        return EvidenceLevel.PARSED_ONLY
    if name_upper.startswith("BMS."):
        return EvidenceLevel.PARSED_ONLY
    return EvidenceLevel.UNSUPPORTED

def get_unsupported_features(features: List[str]) -> List[str]:
    """Filter list of detected features for UNSUPPORTED/PARSED_ONLY items."""
    return [f for f in features if classify_feature(f) in (EvidenceLevel.UNSUPPORTED, EvidenceLevel.PARSED_ONLY)]

def get_all_by_level(level: str) -> List[str]:
    """Return list of capability keys at the given evidence level."""
    return [k for k, v in CAPABILITIES.items() if v["evidence_level"] == level]
