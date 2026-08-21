from .observations import ExecutionObservation
from .contracts import ExecutionContract
from .results import ComparisonResult
from .normalization import NormalizationRules
import re

class EquivalenceEngine:
    @staticmethod
    def compare(
        obs_cobol: ExecutionObservation,
        obs_java: ExecutionObservation,
        contract: ExecutionContract
    ) -> ComparisonResult:
        result = ComparisonResult(schema_version="1.0")
        
        # 1. Verify scenario ID match
        if obs_cobol.scenario_id != obs_java.scenario_id:
            result.status = "UNVERIFIED"
            result.checks["output_presence"] = "UNVERIFIED"
            result.differences.append({
                "type": "scenario_id_mismatch",
                "expected": obs_cobol.scenario_id,
                "actual": obs_java.scenario_id,
                "reason": "Observations belong to different scenarios."
            })
            return result

        result.evidence = {
            "scenario_id": obs_cobol.scenario_id,
            "baseline_status": obs_cobol.execution_status,
            "java_status": obs_java.execution_status
        }

        # Initialize all checks to PASS by default. Only expected checks will be evaluated.
        result.checks = {
            "output_presence": "PASS",
            "file_set": "PASS",
            "file_contents": "PASS",
            "record_counts": "PASS",
            "stdout": "PASS",
            "stderr": "PASS",
            "exit_code": "PASS",
            "database_state": "PASS",
        }

        expected_modes = contract.expected_output_modes

        # Normalize database states to map format for compatibility
        def normalize_db_state(db_state):
            if not isinstance(db_state, dict):
                return {}
            if "db_type" in db_state:
                context = db_state.get("context_id", "default")
                return {context: db_state}
            return db_state

        cobol_db_state = normalize_db_state(obs_cobol.database_state)
        java_db_state = normalize_db_state(obs_java.database_state)

        # 2. Exit code parity check
        if "EXPECTED_EXIT_STATUS" in expected_modes:
            result.checks["exit_code"] = "UNVERIFIED"
            cobol_rc = obs_cobol.exit_code
            java_rc = obs_java.exit_code
            
            is_equivalent = (cobol_rc == java_rc)
            if not is_equivalent:
                allowed_equivs = contract.exit_code_parities.get(str(cobol_rc))
                if allowed_equivs and java_rc in allowed_equivs:
                    is_equivalent = True
                    result.normalizations.append({
                        "type": "exit_code_parities_exception",
                        "baseline_exit_code": cobol_rc,
                        "java_exit_code": java_rc,
                        "reason": "Exit code mismatch explicitly allowed by contract."
                    })
            
            if is_equivalent:
                result.checks["exit_code"] = "PASS"
            else:
                result.checks["exit_code"] = "FAIL"
                result.differences.append({
                    "type": "exit_code_mismatch",
                    "expected": cobol_rc,
                    "actual": java_rc,
                    "reason": "Exit status difference detected."
                })

        # 3. Observables presence & comparison
        cobol_files = set(obs_cobol.files.keys())
        java_files = set(obs_java.files.keys())
        all_observed_files = cobol_files | java_files

        if "EXPECTED_NO_OUTPUT" in expected_modes:
            result.checks["output_presence"] = "UNVERIFIED"
            result.checks["file_set"] = "UNVERIFIED"
            if not all_observed_files:
                result.checks["output_presence"] = "PASS"
                result.checks["file_set"] = "PASS"
            else:
                result.checks["output_presence"] = "FAIL"
                result.checks["file_set"] = "FAIL"
                result.differences.append({
                    "type": "unexpected_output_files",
                    "expected": [],
                    "actual": list(all_observed_files),
                    "reason": "Output files produced when none were expected."
                })
        elif "EXPECTED_FILES" in expected_modes:
            result.checks["output_presence"] = "UNVERIFIED"
            result.checks["file_set"] = "UNVERIFIED"
            result.checks["file_contents"] = "UNVERIFIED"
            result.checks["record_counts"] = "UNVERIFIED"
            
            if not all_observed_files:
                result.checks["output_presence"] = "FAIL"
                result.checks["file_set"] = "FAIL"
                result.checks["file_contents"] = "FAIL"
                result.checks["record_counts"] = "FAIL"
                result.differences.append({
                    "type": "missing_output_files",
                    "expected": contract.required_files,
                    "actual": [],
                    "reason": "No output files produced when outputs were expected."
                })
            else:
                result.checks["output_presence"] = "PASS"
                required = set(contract.required_files)
                missing = required - java_files
                extra = java_files - required - set(contract.optional_files)

                if missing or extra:
                    result.checks["file_set"] = "FAIL"
                    if missing:
                        result.differences.append({
                            "type": "missing_required_files",
                            "expected": list(required),
                            "actual": list(java_files),
                            "reason": f"Required files missing: {list(missing)}"
                        })
                    if extra:
                        result.differences.append({
                            "type": "unexpected_extra_files",
                            "expected": list(required),
                            "actual": list(java_files),
                            "reason": f"Extra files generated: {list(extra)}"
                        })
                else:
                    result.checks["file_set"] = "PASS"

                norm = NormalizationRules(contract.normalization_rules)
                content_fail = False
                record_fail = False
                
                for key in sorted(all_observed_files):
                    b_status = obs_cobol.files.get(key, "MISSING")
                    j_status = obs_java.files.get(key, "MISSING")

                    if b_status == "MISSING" or j_status == "MISSING":
                        content_fail = True
                        continue

                    if key in contract.expected_empty_files:
                        if b_status == "PRESENT_EMPTY" and j_status == "PRESENT_EMPTY":
                            continue
                        else:
                            content_fail = True
                            result.differences.append({
                                "file": key,
                                "type": "empty_status_mismatch",
                                "expected": "PRESENT_EMPTY",
                                "actual": f"baseline: {b_status}, java: {j_status}",
                                "reason": "Expected empty file status mismatch."
                            })
                            continue

                    if b_status == "PRESENT_NONEMPTY" and j_status == "PRESENT_EMPTY":
                        content_fail = True
                        result.differences.append({
                            "file": key,
                            "type": "nonempty_status_mismatch",
                            "expected": "PRESENT_NONEMPTY",
                            "actual": "PRESENT_EMPTY",
                            "reason": "File is empty in Java execution but non-empty in baseline."
                        })
                        continue

                    # If this file has logical database comparison, check that instead of physical bytes comparison
                    b_db_state = cobol_db_state.get(key)
                    j_db_state = java_db_state.get(key)
                    if b_db_state and j_db_state:
                        logical_v = j_db_state.get("normalization_metadata", {}).get("logical_verdict")
                        if logical_v == "LOGICAL_MATCH":
                            # Matches logically! Add to normalization list to indicate match
                            result.normalizations.append({
                                "type": "indexed_logical_normalization",
                                "artifact": key,
                                "reason": "Indexed file physical format variance normalized via database record comparison."
                            })
                            continue
                        elif logical_v == "LOGICAL_MISMATCH":
                            content_fail = True
                            result.differences.append({
                                "file": key,
                                "type": "logical_database_mismatch",
                                "reason": "Database logical verification failed."
                            })
                            continue

                    b_raw = obs_cobol.file_contents.get(key, "")
                    j_raw = obs_java.file_contents.get(key, "")
                    
                    b_norm = norm.normalize(b_raw, key, result.normalizations)
                    j_norm = norm.normalize(j_raw, key, result.normalizations)

                    if b_norm != j_norm:
                        content_fail = True
                        result.differences.append({
                            "file": key,
                            "type": "content_difference",
                            "expected": b_norm[:500],
                            "actual": j_norm[:500],
                            "reason": "File contents mismatch after normalization."
                        })

                    b_rec = obs_cobol.record_counts.get(key, 0)
                    j_rec = obs_java.record_counts.get(key, 0)
                    if b_rec != j_rec:
                        record_fail = True
                        result.differences.append({
                            "file": key,
                            "type": "record_count_mismatch",
                            "expected": b_rec,
                            "actual": j_rec,
                            "reason": "File record counts mismatch."
                        })

                result.checks["file_contents"] = "FAIL" if content_fail else "PASS"
                result.checks["record_counts"] = "FAIL" if record_fail else "PASS"

        # 4. Stdout / Stderr comparison
        if "EXPECTED_STDOUT" in expected_modes:
            result.checks["stdout"] = "UNVERIFIED"
            b_stdout = obs_cobol.stdout
            j_stdout = obs_java.stdout
            norm = NormalizationRules(contract.normalization_rules)
            b_std_norm = norm.normalize(b_stdout, "stdout", result.normalizations)
            j_std_norm = norm.normalize(j_stdout, "stdout", result.normalizations)

            if b_std_norm == j_std_norm:
                result.checks["stdout"] = "PASS"
            else:
                result.checks["stdout"] = "FAIL"
                result.differences.append({
                    "type": "stdout_mismatch",
                    "expected": b_std_norm[-500:],
                    "actual": j_std_norm[-500:],
                    "reason": "Stdout print mismatch."
                })

        # 5. Database state comparison
        if "EXPECTED_DATABASE_STATE" in expected_modes:
            result.checks["database_state"] = "UNVERIFIED"
            
            db_fail = False
            for key in sorted(cobol_db_state.keys() | java_db_state.keys()):
                b_db = cobol_db_state.get(key, {})
                j_db = java_db_state.get(key, {})
                if b_db.get("db_type") != j_db.get("db_type"):
                    db_fail = True
                    result.differences.append({
                        "file": key,
                        "type": "database_type_mismatch",
                        "expected": b_db.get("db_type"),
                        "actual": j_db.get("db_type"),
                        "reason": "Database vendor type mismatch."
                    })
                
                if b_db.get("affected_tables") != j_db.get("affected_tables"):
                    db_fail = True
                    result.differences.append({
                        "file": key,
                        "type": "database_tables_mismatch",
                        "expected": b_db.get("affected_tables"),
                        "actual": j_db.get("affected_tables"),
                        "reason": "Database affected tables mismatch."
                    })

            result.checks["database_state"] = "FAIL" if db_fail else "PASS"

        # 6. Overall Status Verdict
        any_fail = any(v == "FAIL" for v in result.checks.values())
        any_unverified = any(v == "UNVERIFIED" for v in result.checks.values())

        if any_fail:
            result.status = "FAIL"
        elif any_unverified:
            result.status = "UNVERIFIED"
        else:
            result.status = "PASS"

        return result
