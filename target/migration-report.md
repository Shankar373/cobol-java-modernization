# COBOL -> Java Migration Report

- **repo**: `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\legacy`
- **target project**: `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target`
- **run at**: 2026-08-18T16:34:52+00:00 (UTC)
- **overall verdict**: **PASS**

## 1. Program discovery

| source | PROGRAM-ID | lines | transpiled |
|---|---|---|---|
| src/CCLEGACYX.cob | CCLEGACYX | 30 | yes |
| src/CCLOAD01.cob | CCLOAD01 | 70 | yes |
| src/CCMAIN01.cob | CCMAIN01 | 18 | yes |
| src/CCPROC01.cob | CCPROC01 | 130 | yes |
| src/CCREPT01.cob | CCREPT01 | 65 | yes |

- format detected: `free`  |  entry point: `CCMAIN01`  |  copybook dirs: `['copybooks']`

## 2. Transpilation (cobj)

- engine: opensource COBOL 4J (`opensourcecobol/opensourcecobol4j:2.0.0`), all-at-once rc=0
## 3. Generated Java

- 5 source files, 3234 LOC in `generated/`

## 4. Runtime dependencies preserved

- `libcobj.jar` (engine `opensourcecobol/opensourcecobol4j:2.0.0`), 19285213 bytes, sha256 `e087bd9e65c28972666f38775aa00fa3d8f5c12deb52ffb92935551110500b93`

## 5. Target project

| artifact | path |
|---|---|
| generated sources / classes | `generated/` |
| runtime library | `libcobj.jar` |
| run script (docker) | `run-java.sh` / `run-java.bat` |
| manifest | `manifest.json` |

## 6. Legacy baseline

- engine: GnuCOBOL `cobc (GnuCOBOL) 3.1.2.0` (`hurriedreformist/gnucobol:3.1-builder`), build rc=0, run rc=0
- console: `CLAIMSCORE ENTERPRISE NIGHTLY BATCH
CLAIMS PROCESSED: 0000007
CLAIMSCORE NIGHTLY BATCH COMPLETED`

- baseline files: 5

## 7. Java execution

- command: `java -cp generated:libcobj.jar CCMAIN01 `  rc=0
- console: `CLAIMSCORE ENTERPRISE NIGHTLY BATCH`
- console: `CLAIMS PROCESSED: 0000007`
- console: `CLAIMSCORE NIGHTLY BATCH COMPLETED`

- results files: 5

## 8. Comparison (baseline vs Java)

| file | verdict | mode | baseline bytes | java bytes | diff detail |
|---|---|---|---|---|---|
| data/out/claim-audit.dat | exact | exact | 884 | 884 |  |
| data/out/claim-exceptions.dat | exact | exact | 663 | 663 |  |
| data/out/eod-claims-report.txt | exact | normalized | 344 | 344 |  |
| data/work/customer.dat | differ | exact | 8192 | 36864 | binary: sizes 8192 vs 36864 bytes, first diff at offset 0 |
| data/work/policy.dat | differ | exact | 8192 | 36864 | binary: sizes 8192 vs 36864 bytes, first diff at offset 0 |

- summary: {'baseline-only': 0, 'exact': 3, 'differ': 2, 'normalized': 0, 'java-only': 0}

## 9. Semantic checks

- [PASS] `data/out/claim-audit.dat` (comp3): expected `['95000.00', '35000.00', '295000.00', '300000.00']` -> actual `['95000.00', '35000.00', '295000.00', '300000.00']`
- [PASS] `data/out/eod-claims-report.txt` (regex): expected `4` -> actual `0000004`
- [PASS] `data/out/eod-claims-report.txt` (regex): expected `3` -> actual `0000003`
- [PASS] `data/out/eod-claims-report.txt` (regex): expected `2` -> actual `0000002`

## 10. Checkpoint

- per-stage state persisted in `state.json` (resume from any completed stage)


## Known engine deviations

- **Indexed file containers differ by engine.** GnuCOBOL 3.1 writes single-file embedded-index `*.dat` (8,192 B here); COBOL 4J backs indexed files with SQLite (36,864 B files, "SQLite format 3" header). Same logical records from the same loader, different on-disk layout - `data/work` byte parity is excluded from the pass/fail criterion by design.
- **STRING of COMP-3 is byte-identical across engines (measured).** `data/out/claim-audit.dat` matches exactly; the packed-decimal amounts still decode to the expected settlement values.
- **Baseline engine must be pinned to GnuCOBOL 3.1.x.** GnuCOBOL 4.0 refuses to compile this program (`STRING item ... must be USAGE DISPLAY or NATIONAL`); the transpiled Java has no such limitation.
- **STRING does not clear the target buffer** (trailing `REPORT` bytes in `0000004REPORT`). Present identically in both engines - preserved behavior, not a regression.
- **Real transpiled logic, not stubs.** The generated Java implements the settlement COMPUTE and the P001/P002/P003 EVALUATE as actual control flow - verified by the PASS verdict and exact output parity.