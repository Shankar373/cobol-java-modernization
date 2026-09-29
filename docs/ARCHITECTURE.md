# Platform Architecture

This document describes the compiler and generator design of the COBOL-to-Java Modernization Platform.

> **Deterministic architecture (no LLM):** the executable path is
> `modernize/lexer.py` → `modernize/parser.py` → `modernize/semantic_ir.py` →
> `modernize/control_flow.py` → `modernize/native_generator.py`, orchestrated
> by `cobol_migrate.py` / `modernize/native_pipeline.py`. There is no LLM,
> provider, or learned model anywhere in that path. OpenSource COBOL 4J
> (`cobj` + `libcobj.jar` / `jp.osscons`) is implemented only as the Track-A
> verification gate (`stage_transpile`/`stage_collect` in `cobol_migrate.py`
> using `opensourcecobol/opensourcecobol4j:2.0.0`). `z390`/`Hercules`/`ICU4J`
> are test-only reference oracles under `tools/reference_runtimes/`, never
> production dependencies. There is no external transformer abstraction in
> the executable path; the "deterministic transformer" in
> `docs/PHASE_2_ARCHITECTURE_V2.md` is a proposed/future target design.

---

## 1. Multi-Track Architecture

To support both verification and modernization paths, the platform compiles target repositories into two distinct folders in the final ZIP archive:

```
target/
├── transpiled/ (Track A - Emulated)
│   ├── src/main/java/ (Uses jp.osscons wrappers)
│   └── lib/libcobj.jar
└── modernized/ (Track B - Native Java Spring Boot)
    ├── src/main/java/ (Direct native Java types)
    └── pom.xml (Zero libcobj runtime dependencies)
```

### Track A: Emulated Path
*   **Purpose**: Legacy verification gate (Gate 1).
*   **Translation**: Executes the OpenSourceCOBOL4J `cobj` toolchain in Docker (`opensourcecobol/opensourcecobol4j:2.0.0`) to generate emulated Java bound to `libcobj.jar` / `jp.osscons` wrappers (see `cobol_migrate.py` `DEFAULT_COBJ_IMAGE`, `STAGES["transpile"]`).
*   **Execution**: Validates logic parity against the GnuCOBOL baseline. Track A is a verification oracle only; its emulation runtime never ships in Track-B output.

### Track B: Native Java Path
*   **Purpose**: Target decoupled enterprise code.
*   **Translation**: Deterministic native generator (`modernize/parser.py` → `modernize/semantic_ir.py` → `modernize/native_generator.py`) mapping variables to Java primitives (`int`, `long`, `String`), `BigDecimal`, and pure-Java helpers (`CobolNumeric`, `CobolRef`, `CobolFormatHelper`). No `libcobj.jar`, no `jp.osscons`, no OpenSourceCOBOL4J runtime in generated code.
*   **Decoupled Frameworks**: Generates REST Controllers, Spring Batch tasklets/steps, and standard Spring Data JPA interfaces.
*   **Determinism**: Same inputs produce byte-identical sources. No LLM participates in the executable transformation path.

---

## 2. Compiler Subsystem Components

```
COBOL Source
   │
   ▼
[Lexer] ──(Token Stream)──► [Parser] ──(Semantic AST)──► [Control Resolver]
                                                            │
                                                            ▼
                                                     [Semantic IR]
                                                            │
                                                            ▼
                                                   [Native Generator]
                                                            │
                                                            ▼
                                                   Spring Boot Project
```

1.  **Lexer (`modernize/lexer.py`)**: Supports copybook resolution, continuation line normalization, comment stripping, and free/fixed margin detection.
2.  **Parser (`modernize/parser.py`)**: Maps token sequences to custom AST statement blocks.
3.  **Semantic IR (`modernize/semantic_ir.py`)**: Normalizes scopes, paragraphs, and data structures.
4.  **Control Flow (`modernize/control_flow.py`)**: Resolves implicit loops, break conditions, and GO TO paragraph sequences.
5.  **Native Generator (`modernize/native_generator.py`)**: Emits type-safe native Java classes.
