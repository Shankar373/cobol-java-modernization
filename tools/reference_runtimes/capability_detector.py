"""Workload Capability Detector for COBOL & Mainframe Sources."""

import json
import os
import re
from typing import Any, Dict, List, Set


class WorkloadCapabilityDetector:
    """Scans repository sources to determine required mainframe subsystems and capability tiers."""

    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir

    def scan_workload(self) -> Dict[str, Any]:
        """Perform comprehensive static scan across all COBOL, Copybook, and JCL sources."""
        requires_batch = True
        requires_sql = False
        requires_vsam = False
        requires_cics = False
        requires_ebcdic = False
        requires_jcl = False

        scanned_files = []
        indicators = {
            "sql_statements": 0,
            "cics_commands": 0,
            "vsam_files": 0,
            "ebcdic_clauses": 0,
            "jcl_jobcards": 0,
        }

        for root, _, files in os.walk(self.repo_dir):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in (".cob", ".cbl", ".cpy", ".jcl", ".txt", ".pco", ".sqb") or "jcl" in f.lower():
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, self.repo_dir).replace("\\", "/")
                    scanned_files.append(rel_path)
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="replace") as fh:
                            content = fh.read().upper()
                            
                            if "EXEC SQL" in content:
                                requires_sql = True
                                indicators["sql_statements"] += content.count("EXEC SQL")

                            if "EXEC CICS" in content:
                                requires_cics = True
                                indicators["cics_commands"] += content.count("EXEC CICS")

                            if "ORGANIZATION IS INDEXED" in content or "ORGANIZATION INDEXED" in content or "ORGANIZATION RELATIVE" in content:
                                requires_vsam = True
                                indicators["vsam_files"] += 1

                            if "EBCDIC" in content or "COLLATING SEQUENCE IS" in content or "CODE-SET" in content:
                                requires_ebcdic = True
                                indicators["ebcdic_clauses"] += 1

                            if "//" in content and ("JOB " in content or "EXEC " in content):
                                requires_jcl = True
                                indicators["jcl_jobcards"] += content.count("JOB ")
                    except Exception:
                        pass

        # Determine required reference environment tier
        required_environments = ["GnuCOBOL"]
        if requires_vsam:
            required_environments.append("zVSAM_Reference")
        if requires_cics:
            required_environments.append("zCICS_Reference")
        if requires_ebcdic:
            required_environments.append("ICU4J_EBCDIC")
        if requires_sql:
            required_environments.append("Relational_Database")
        if requires_jcl:
            required_environments.append("JCL_ExecutionContext")

        manifest = {
            "schema_version": "1.0",
            "repository": os.path.abspath(self.repo_dir).replace("\\", "/"),
            "scanned_files_count": len(scanned_files),
            "requires": {
                "batch": requires_batch,
                "sql": requires_sql,
                "vsam": requires_vsam,
                "cics": requires_cics,
                "ebcdic": requires_ebcdic,
                "jcl": requires_jcl,
            },
            "indicators": indicators,
            "required_reference_environments": required_environments,
            "scanned_files": scanned_files,
        }
        return manifest

    def write_manifest(self, out_dir: str) -> str:
        """Write WORKLOAD_CAPABILITY_MANIFEST.json to out_dir."""
        os.makedirs(out_dir, exist_ok=True)
        manifest = self.scan_workload()
        manifest_path = os.path.join(out_dir, "WORKLOAD_CAPABILITY_MANIFEST.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return manifest_path
