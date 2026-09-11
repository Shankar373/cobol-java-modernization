> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Remediation Baseline Snapshot

- **Repository:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`
- **Branch:** `integration/successor-verified-improvements`
- **Commit SHA:** `2c070615f34057a3616e023dab0850c813188a62`
- **Timestamp:** 2026-09-01T23:10:00+05:30 (UTC: 2026-09-01T17:40:00Z)

## Toolchain Baseline
- **Python:** `Python 3.14.3`
- **Java Runtime:** `OpenJDK 25.0.3` (Eclipse Adoptium Temurin-25.0.3+9)
- **Java Compiler:** `javac 25.0.3`
- **Maven:** `Apache Maven 3.9.16`
- **Docker:** `Docker version 29.6.2, build dfc4efb`
- **Operating System:** `Windows 11 (10.0, amd64)`

## Pre-Remediation Test Baseline
- **Total Test Count:** 678 tests
- **Passed:** 663
- **Failed:** 4 (Fail-closed baseline status assertions)
- **Skipped:** 11

## Golden Repository Baseline
- **Golden Repo #1 (`mentor_cobol_golden_repo.zip` - GOLDENPAY):**
  - Gate 1: **PASS** (32 bytes exact, SHA-256 `aa752eea4445308ea4ad065b337c1cfc285d3e1f8cdce2e2ebcc1cd90c3c08ad`)
  - Gate 2: **PASS** (32 bytes exact, SHA-256 `aa752eea4445308ea4ad065b337c1cfc285d3e1f8cdce2e2ebcc1cd90c3c08ad`)
- **Golden Repo #2 (`mentor_cobol_test_repo_02.zip` - INVENTORY01):**
  - Gate 1: **PASS** (88 bytes exact, SHA-256 `4127a31798f6bae5c4785148cd4c1e447c0382ad60fd2b8955111760f986c251`)
  - Gate 2: **PASS** (88 bytes exact, SHA-256 `4127a31798f6bae5c4785148cd4c1e447c0382ad60fd2b8955111760f986c251`)

## Known Remediation Target
- **BUG-02 (P1):** Generic Spring Batch sequential reader/processor EOF synchronization causing duplicate last-record processing on generic flat-file loops (discovered in `UNSEEN01`).
