"""Cryptographic Manifest and Artifact Integrity Engine.

Generates SHA-256 manifests for source inputs, generated Java artifacts,
compiled binaries, baseline logs, and differential verdicts to ensure
tamper-evident, zero-assumption verification trails.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def compute_sha256(path_or_bytes: Union[str, Path, bytes]) -> str:
    """Compute hex-encoded SHA-256 digest of a file or byte buffer."""
    hasher = hashlib.sha256()
    if isinstance(path_or_bytes, bytes):
        hasher.update(path_or_bytes)
    else:
        path = Path(path_or_bytes)
        if not path.is_file():
            raise FileNotFoundError(f"File not found for hash calculation: {path}")
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
    return hasher.hexdigest()


def scan_directory_hashes(root_dir: Union[str, Path], extensions: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """Recursively scan a directory and compute relative path SHA-256 digests."""
    root = Path(root_dir)
    results = {}
    if not root.is_dir():
        return results

    for p in root.rglob("*"):
        if p.is_file():
            if extensions is not None and p.suffix.lower() not in extensions:
                continue
            rel_path = p.relative_to(root).as_posix()
            try:
                sha = compute_sha256(p)
                size = p.stat().st_size
                results[rel_path] = {
                    "sha256": sha,
                    "size_bytes": size,
                    "modified_iso": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
                }
            except Exception as e:
                results[rel_path] = {"error": str(e)}
    return results


def generate_manifest(
    repo_path: Union[str, Path],
    out_path: Union[str, Path],
    workload_name: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate complete cryptographic manifest for a modernization run."""
    repo = Path(repo_path)
    out = Path(out_path)

    input_extensions = [".cob", ".cbl", ".cpy", ".jcl", ".bms", ".sql", ".dat", ".json"]
    java_extensions = [".java", ".class", ".jar"]

    manifest = {
        "manifest_version": "2.0.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "workload": workload_name or repo.name,
        "repo_path": str(repo.resolve()),
        "output_path": str(out.resolve()),
        "source_inputs": scan_directory_hashes(repo, extensions=input_extensions),
        "generated_artifacts": scan_directory_hashes(out, extensions=java_extensions),
        "baseline_evidence": scan_directory_hashes(out / "baseline" if (out / "baseline").exists() else out),
        "metadata": extra_metadata or {},
    }

    # Compute top-level manifest hash
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
    manifest["manifest_sha256"] = compute_sha256(manifest_bytes)
    return manifest


def write_manifest_file(manifest: Dict[str, Any], output_file: Union[str, Path]) -> Path:
    """Save manifest to JSON file."""
    out_file = Path(output_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return out_file
