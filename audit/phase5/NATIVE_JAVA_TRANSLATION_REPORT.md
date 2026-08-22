# Phase 5 Native Java Translation Report

This report outlines the architecture, implementation details, and verification stages of the direct SemanticIR-to-Java translation pipeline, which is fully decoupled from legacy runtime components.

## 1. Pipeline Architecture

The translation pipeline operates as an independent modernization path activated by the `--native-java` flag. It processes the repository through a series of discrete stages:
1. **Discovery**: Scans source files and copybooks to identify the call graph and physical file assignments.
2. **Parsing**: Constructs a structured SemanticIR representation of COBOL constructs.
3. **Type Mapping**: Generically maps COBOL picture clauses and USAGE clauses to standard Java types.
4. **Data Model Generation**: Generates POJO-like classes containing standard Java fields with getters/setters.
5. **Statement Translation**: Translates SemanticIR node expressions, conditions, and statements into corresponding Java logic.
6. **File I/O Method Generation**: Builds native Java fixed-width readers/writers using standard standard-library buffers (`BufferedReader` / `BufferedWriter`).
7. **Traceability Generation**: Compiles the source-to-target manifest coordinates.

---

## 2. Technical Implementation Details

### SemanticIR → Native Java Translation
SemanticIR statements map to direct Java statements. Unsupported statements (e.g. unknown inline extensions or legacy calls) are generated as comment warnings (`// Unsupported statement: ...`) rather than causing pipeline compilation failures.

### Type Mapping
- `PIC X(n)` maps to `String`
- `PIC 9(n)` maps to `int` or `long` depending on precision (length <= 9 -> `Integer`, else `Long`).
- `PIC 9(n)V9(n)` and `PIC S9(n)V9(n)` map to `BigDecimal`.
- `COMP` / `COMP-3` map to numeric representations (primarily `BigDecimal` or standard primitives).

### Data Model Generation
The generated Java files declare raw fields matching mapped types (e.g. `public String wsEof = "N";`), removing all wrapper dependencies (like `CobolField` or `opensourcecobol4j` annotations).

### Statement Translation
- **MOVE**: Translates values/literals to direct assignments, format formatting, or `BigDecimal.ZERO` depending on targets.
- **COMPUTE / Arithmetic**: Converts `ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE` to BigDecimal method call chains (`.add()`, `.subtract()`, `.divide()`) or native operators.
- **IF / PERFORM UNTIL**: Translates conditions to standard Java branches, mapping string checks to `.equals()`.

### File I/O & Mainframe Signed Zoned Representation
To achieve physical-output equivalence, the file writer and reader implement zoned-decimal trailing sign formatting. Trailing negative digits `0-9` map to ASCII `p-y`. This translation occurs inside the generated `formatSigned()` and `parseSigned()` helpers, preserving exact byte matches with GnuCOBOL baseline reports.

### CALL Handling
Static and dynamic calls map to target instantiated class executions. Dynamic calls map variable target lookups to conditional executions:
```java
String targetProg_prog_name = prog_name.trim().toUpperCase();
if (targetProg_prog_name.equals("SUBPROG1")) {
    Subprog1 subprog1 = new Subprog1();
    ...
}
```

---

## 3. Dependency Isolation

The dependency scanner (`stage_dependency_gate`) audits all generated files for the presence of:
- `libcobj` / `libcobj.jar`
- `jp.osscons.*`
- `CobolField` / `CobolResolve`
- `opensourcecobol4j` runtime components

Any occurrence flags the build as `NATIVE_JAVA_BLOCKED` to ensure 100% decoupling from legacy runtime dependencies.

---

## 4. Known Limitations

1. **Unsupported Statements**: Non-standard COBOL verbs that lack direct Java equivalents (e.g. specialized SORT/MERGE or interactive raw console reads) are omitted with comment placeholders.
2. **Variable Overlap (REDEFINES)**: Overlapping storage structures are mapped to distinct fields, meaning that modifications to redefined fields are not automatically synchronized unless explicitly modeled via getters/setters.
