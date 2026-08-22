# COBOL -> Java Migration Report

- **repo**: `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\legacy`
- **target project**: `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target`
- **run at**: 2026-08-21T12:13:02+00:00 (UTC)
- **overall verdict**: **PASS**

## Source Immutability

| file | ingest hash | current hash | status |
|---|---|---|---|
| src/CCLEGACYX.cob | `791f1b6774f34ba5...` | `aa288dfd01ef5ae3...` | **MODIFIED** |
| src/CCLOAD01.cob | `448abf1fa5aff4b6...` | `989708dcf1ca542e...` | **MODIFIED** |
| src/CCMAIN01.cob | `c4afcb139c81bdac...` | `d74d2ebf95260dcb...` | **MODIFIED** |
| src/CCPROC01.cob | `3ac7548dab0e790f...` | `a30343c37e0de18b...` | **MODIFIED** |
| src/CCREPT01.cob | `2113d2b5fb3845ac...` | `2fcc5adcb69ed6c6...` | **MODIFIED** |
| copybooks/CC-CLAIM.cpy | `9351c86a538c9161...` | `e370a5c473e783ed...` | **MODIFIED** |
| copybooks/CC-CONSTANTS.cpy | `3c61314e02b65430...` | `398909a0fe828d9b...` | **MODIFIED** |
| copybooks/CC-CUSTOMER.cpy | `de973e92e6b8f1ed...` | `9dcc72b9855601c5...` | **MODIFIED** |
| copybooks/CC-POLICY.cpy | `f21fc4197e27000f...` | `e620461019da467b...` | **MODIFIED** |

> ⚠️ **9 source file(s) MODIFIED since ingest.**
> Any source change must be recorded as MANUAL SOURCE MODIFICATION.

## 1. Program discovery

| source | PROGRAM-ID | lines | transpiled |
|---|---|---|---|
| src/CCLEGACYX.cob | CCLEGACYX | 30 | yes |
| src/CCLOAD01.cob | CCLOAD01 | 70 | yes |
| src/CCMAIN01.cob | CCMAIN01 | 18 | yes |
| src/CCPROC01.cob | CCPROC01 | 130 | yes |
| src/CCREPT01.cob | CCREPT01 | 65 | yes |

- format detected: `free`  |  entry point: `CCMAIN01`  |  copybook dirs: `['copybooks']`

## 2. COPYBOOK Dependencies

**src/CCLOAD01.cob**
  - COPY `copybooks/CC-POLICY.cpy` → `copybooks/CC-POLICY.cpy`
  - COPY `copybooks/CC-CUSTOMER.cpy` → `copybooks/CC-CUSTOMER.cpy`
**src/CCPROC01.cob**
  - COPY `copybooks/CC-POLICY.cpy` → `copybooks/CC-POLICY.cpy`
  - COPY `copybooks/CC-CLAIM.cpy` → `copybooks/CC-CLAIM.cpy`
  - COPY `copybooks/CC-CONSTANTS.cpy` → `copybooks/CC-CONSTANTS.cpy`

## 3. CALL Dependency Graph

**CCMAIN01**
  - CALL `CCLOAD01` (static)
  - CALL `CCPROC01` (static)
  - CALL `CCREPT01` (static)

- Entry point candidates (no callers): `['CCMAIN01', 'CCLEGACYX']`

## 4. File / Dataset Dependencies

| source | logical name | assign path | organization |
|---|---|---|---|
| src/CCLOAD01.cob | POLICY-MASTER | `data/work/policy.dat` | INDEXED |
| src/CCLOAD01.cob | CUSTOMER-MASTER | `data/work/customer.dat` | INDEXED |
| src/CCPROC01.cob | CLAIM-IN | `data/in/claims.dat` | LINE |
| src/CCPROC01.cob | POLICY-MASTER | `data/work/policy.dat` | INDEXED |
| src/CCPROC01.cob | AUDIT-OUT | `data/out/claim-audit.dat` | LINE |
| src/CCPROC01.cob | EXCEPTION-OUT | `data/out/claim-exceptions.dat` | LINE |
| src/CCREPT01.cob | AUDIT-IN | `data/out/claim-audit.dat` | LINE |
| src/CCREPT01.cob | EXCEPTION-IN | `data/out/claim-exceptions.dat` | LINE |
| src/CCREPT01.cob | REPORT-OUT | `data/out/eod-claims-report.txt` | LINE |

## 5. Transpilation (cobj)

- engine: opensource COBOL 4J (`opensourcecobol/opensourcecobol4j:2.0.0`), all-at-once rc=0
- image digest: `opensourcecobol/opensourcecobol4j@sha256:446bc5abb67cd103b257c2c75909e51395b771ea499034bf512c46bf1796223a`
- 5/5 programs transpiled
## 6. Generated Java

- 5 source files, 3234 LOC in `generated/`

### Per-File Provenance

| source | PROGRAM-ID | source SHA-256 | Java file | Java SHA-256 | class | status |
|---|---|---|---|---|---|---|
| src/CCLEGACYX.cob | CCLEGACYX | `791f1b6774f34ba5...` | CCLEGACYX.java | `fa8500c49643cc39...` | CCLEGACYX.class | ✅ OK |
| src/CCLOAD01.cob | CCLOAD01 | `448abf1fa5aff4b6...` | CCLOAD01.java | `b8b635b4e268726f...` | CCLOAD01.class | ✅ OK |
| src/CCMAIN01.cob | CCMAIN01 | `c4afcb139c81bdac...` | CCMAIN01.java | `414f709391ab3a66...` | CCMAIN01.class | ✅ OK |
| src/CCPROC01.cob | CCPROC01 | `3ac7548dab0e790f...` | CCPROC01.java | `afdec60e88cfca55...` | CCPROC01.class | ✅ OK |
| src/CCREPT01.cob | CCREPT01 | `2113d2b5fb3845ac...` | CCREPT01.java | `3840cfe041a17ab7...` | CCREPT01.class | ✅ OK |

## 7. Runtime dependencies preserved

- `libcobj.jar` (engine `opensourcecobol/opensourcecobol4j:2.0.0`), 19285213 bytes, sha256 `e087bd9e65c28972666f38775aa00fa3d8f5c12deb52ffb92935551110500b93`

## 8. Legacy baseline

- engine: GnuCOBOL `cobc (GnuCOBOL) 3.1.2.0` (`hurriedreformist/gnucobol:3.1-builder`), build rc=0, run rc=0
- console: `CLAIMSCORE ENTERPRISE NIGHTLY BATCH
CLAIMS PROCESSED: 0000007
CLAIMSCORE NIGHTLY BATCH COMPLETED`

- baseline files: 5

## 9. Java execution

- command: `cd /repo && java -cp /target/generated:/target/libcobj.jar CCMAIN01`  rc=0
- console: `CLAIMSCORE ENTERPRISE NIGHTLY BATCH`
- console: `CLAIMS PROCESSED: 0000007`
- console: `CLAIMSCORE NIGHTLY BATCH COMPLETED`

- results files: 5

## 10. Comparison (baseline vs Java)

| file | verdict | mode | baseline bytes | java bytes | logical | diff detail |
|---|---|---|---|---|---|---|
| data/out/claim-audit.dat | exact | exact | 884 | 884 |  |  |
| data/out/claim-exceptions.dat | exact | exact | 663 | 663 |  |  |
| data/out/eod-claims-report.txt | exact | normalized | 344 | 344 |  |  |
| data/work/customer.dat | differ | exact | 8192 | 36864 |  |  |
| data/work/policy.dat | differ | exact | 8192 | 36864 |  |  |

- summary: {'exact': 3, 'normalized': 0, 'differ': 2, 'baseline-only': 0, 'java-only': 0}

## 11. Semantic checks

- [PASS] `data/out/claim-audit.dat` (comp3): expected `['95000.00', '35000.00', '295000.00', '300000.00']` -> actual `['95000.00', '35000.00', '295000.00', '300000.00']`
- [PASS] `data/out/eod-claims-report.txt` (regex): expected `4` -> actual `0000004`
- [PASS] `data/out/eod-claims-report.txt` (regex): expected `3` -> actual `0000003`
- [PASS] `data/out/eod-claims-report.txt` (regex): expected `2` -> actual `0000002`

## 12. Validate (Gate 2)

- Gate 2 status: **✅ PASSED**
- Detail: Gate 2 PASS — exact parity with GnuCOBOL baseline (4 processed claims, 3 exceptions)
- Claims verified: `4` | Exceptions verified: `3`

## 13. Package

- Package not yet created.

## 14. Checkpoint / Resume

- per-stage state persisted in `state.json` (resume from any completed stage)


## Known Manual Source Modifications

- **src/CCPROC01.cob**: MANUAL SOURCE MODIFICATION (before: `UNKNOWN_original...`, after: `3ac7548dab0e790f...`)


## Known Engine Deviations

- **Indexed file containers differ by engine.** GnuCOBOL 3.1 writes single-file embedded-index `*.dat`; COBOL 4J backs indexed files with SQLite. Same logical records; logical comparison applied where possible.
- **GnuCOBOL 4.0 incompatible** with this source (`STRING item ... must be USAGE DISPLAY`); baseline pinned to GnuCOBOL 3.1.x.
- **STRING of COMP-3 is byte-identical** across engines (verified).
- **Real transpiled logic, not stubs.** Generated Java implements actual control flow — verified by PASS verdict and exact output parity.