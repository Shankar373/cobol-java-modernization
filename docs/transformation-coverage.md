# Transformation Coverage Matrix

This matrix documents the verification status, pipeline locations, and limitations for each legacy COBOL and mainframe construct supported by the transformation engine.

---

## 1. Construct Traceability & Evidence Matrix

### PIC / USAGE
- **Parser Location**: [`modernize/parser.py:parse_data_item`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L657)
- **Semantic IR**: `VARIABLE` / `DATA_ITEM` node properties (`picture`, `usage`, `signed`, `digits`, `scale`).
- **Generator Location**: [`modernize/native_generator.py:get_java_type`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L122)
- **Java Runtime Helper**: None (native Java mappings to `String`, `Integer`, `Long`, `BigDecimal`).
- **Test File(s)**: [`tests/test_native_type_mapping.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_native_type_mapping.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Standard numeric (`PIC 9`), alphanumeric (`PIC X`), and signed numeric (`PIC S9`).
- **Known Limitations**: Implied decimal position (`V`) is mapped to Java `BigDecimal` but relies on division scaling checks. Variables without implied decimal points (`V`) or COMP-3 are optimized into native Java `Integer` or `Long` fast-path primitives, meaning they are bound by standard Java primitive range limits rather than exact zoned-decimal size error overflows.

### COMP-3 (Packed Decimal)
- **Parser Location**: [`modernize/parser.py:parse_data_item`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L689)
- **Semantic IR**: `VARIABLE` (usage="COMP-3" / "PACKED-DECIMAL")
- **Generator Location**: [`modernize/native_generator.py:get_java_type`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L123)
- **Java Runtime Helper**: `parseSigned` / `formatSigned` printed in generated class sources.
- **Test File(s)**: [`tests/test_phase8_arithmetic_errors.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_arithmetic_errors.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: standard COMP-3 definitions.
- **Known Limitations**: Implied sign bits at the end of byte slices are formatted as signed overpunches.

### Arithmetic and Rounding
- **Parser Location**: [`modernize/parser.py:parse_add_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py) (also `parse_subtract_statement`, `parse_multiply_statement`, `parse_divide_statement`)
- **Semantic IR**: `STATEMENT` (kinds: ADD, SUBTRACT, MULTIPLY, DIVIDE) with `rounded` attribute in properties.
- **Generator Location**: [`modernize/native_generator.py:_translate_statement_inner`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: `checkSizeError` helper printed in generated class sources.
- **Test File(s)**: [`tests/test_phase8_arithmetic_errors.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_arithmetic_errors.py), [`tests/test_parity_fixtures.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_parity_fixtures.py)
- **Evidence Level**: `DIFFERENTIALLY_VERIFIED`
- **Supported Subset**: Basic numeric assignments and operations.
- **Known Limitations**: `BigDecimal` divisions without `ROUNDED` clause default to scaling and truncation behavior in the expression translator. Also, divide-by-zero operations produce process-level differences: GnuCOBOL terminates with platform-dependent signals (SIGFPE) and exit code 136, whereas modernized Java terminates cleanly with exit code 1 or standard exception logs.

### MOVE
- **Parser Location**: [`modernize/parser.py:parse_move_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L946)
- **Semantic IR**: `STATEMENT` (statement_type="MOVE") with `sources` and `targets` lists.
- **Generator Location**: [`modernize/native_generator.py:generate_assignment`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L523)
- **Java Runtime Helper**: `padString` helper printed in generated class sources.
- **Test File(s)**: [`tests/test_native_move_multi.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_native_move_multi.py), [`tests/test_parity_fixtures.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_parity_fixtures.py)
- **Evidence Level**: `DIFFERENTIALLY_VERIFIED`
- **Supported Subset**: Text padding, truncation, numeric-to-alphanumeric assignments.
- **Known Limitations**: Group-to-group MOVEs are mapped as string-padded chunk operations.

### COMPUTE
- **Parser Location**: [`modernize/parser.py:parse_compute_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L1003)
- **Semantic IR**: `STATEMENT` (statement_type="COMPUTE") with formula target properties.
- **Generator Location**: [`modernize/native_generator.py:_translate_statement_inner`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: `ExpressionTranslator` maps formulas inline.
- **Test File(s)**: [`tests/test_phase8_expressions.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_expressions.py), [`tests/test_parity_fixtures.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_parity_fixtures.py)
- **Evidence Level**: `DIFFERENTIALLY_VERIFIED`
- **Supported Subset**: standard math expression formats.
- **Known Limitations**: Div-by-zero checks are evaluated inline.

### REDEFINES
- **Parser Location**: [`modernize/parser.py:parse_data_item`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L675)
- **Semantic IR**: `VARIABLE` (redefines="target_var")
- **Generator Location**: [`modernize/native_generator.py:generate_class_source`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L4250)
- **Java Runtime Helper**: Custom formatted getter/setter wrappers.
- **Test File(s)**: [`tests/test_phase8_redefines.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_redefines.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Base level numeric and string redefinitions.
- **Known Limitations**: Redefinitions that overlap dynamic tables are not backed by byte-buffer memory slices.

### OCCURS and OCCURS DEPENDING ON
- **Parser Location**: [`modernize/parser.py:parse_data_item`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L767)
- **Semantic IR**: `VARIABLE` (`occurs`, `occurs_min`, `occurs_max`, `depending_on`)
- **Generator Location**: [`modernize/native_generator.py:_translate_subscripts`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: `checkBounds` helper printed in generated class sources.
- **Test File(s)**: [`tests/test_native_occurs.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_native_occurs.py), [`tests/test_phase8_occurs_depending.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_occurs_depending.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Multi-dimensional OCCURS arrays and dynamically bounded arrays.
- **Known Limitations**: Subscripts are converted from 1-based indexing to 0-based.

### Copybooks
- **Parser Location**: [`modernize/lexer.py:preprocess_copybooks`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/lexer.py#L70)
- **Semantic IR**: None (preprocessor expands copies in lexer before parsing starts).
- **Generator Location**: Inline statements.
- **Java Runtime Helper**: None.
- **Test File(s)**: [`tests/test_lexer.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_lexer.py), [`tests/test_proleap_copybooks.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_proleap_copybooks.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Inline copy files resolved via local copybook path lists.
- **Known Limitations**: Bypasses dynamic path substitutions.

### File Handling (Line Sequential Write)
- **Parser Location**: [`modernize/parser.py:parse_write_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py)
- **Semantic IR**: `STATEMENT` (WRITE)
- **Generator Location**: [`modernize/native_generator.py:generate_io_methods`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L2749)
- **Java Runtime Helper**: `BufferedWriter`
- **Test File(s)**: [`tests/test_parity_fixtures.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_parity_fixtures.py)
- **Evidence Level**: `DIFFERENTIALLY_VERIFIED`
- **Supported Subset**: Writing ASCII/UTF-8 line-sequential text records with trailing whitespace trimmed.
- **Known Limitations**: Does not support EBCDIC conversions or record descriptor words (RDW) for this mode.

### File Handling (Sequential / Relative / Indexed Access)
- **Parser Location**: [`modernize/parser.py:parse_read_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L1304) (and other IO statements)
- **Semantic IR**: `STATEMENT` (READ/WRITE/REWRITE/DELETE) with file properties.
- **Generator Location**: [`modernize/native_generator.py:generate_io_methods`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L2749)
- **Java Runtime Helper**: `BufferedReader` / `BufferedWriter` for sequential I/O, `JdbcTemplate` for SQL-backed relative/indexed files.
- **Test File(s)**: [`tests/test_phase8_file_semantics.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_file_semantics.py), [`tests/test_vsam_rrds.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_vsam_rrds.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Fixed-length sequential, database emulated relative random access, and indexed random access.
- **Known Limitations**: Trailing space trimming must not be applied to fixed-width or binary records. Mapped to embedded H2 tables or sequential text files.

### FILE STATUS
- **Parser Location**: [`modernize/parser.py:parse_file_control`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L522)
- **Semantic IR**: `FILE_CONTROL` (property `status_var`)
- **Generator Location**: [`modernize/native_generator.py:generate_io_methods`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L2749)
- **Java Runtime Helper**: Inline assignments (e.g. `ws_status = "00"`).
- **Test File(s)**: [`tests/test_phase8_file_semantics.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_file_semantics.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Status codes `"00"`, `"10"`, `"23"`, `"35"`.
- **Known Limitations**: Standard status variables must be defined in WORKING-STORAGE.

### PERFORM and PERFORM THRU
- **Parser Location**: [`modernize/parser.py:parse_perform_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L1119)
- **Semantic IR**: `STATEMENT` (statement_type="PERFORM") with `thru_paragraph` attributes.
- **Generator Location**: [`modernize/native_generator.py:_translate_statement_inner`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: Paragraph indexing execution loop.
- **Test File(s)**: [`tests/test_native_perform_varying.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_native_perform_varying.py), [`tests/test_native_paragraph_control.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_native_paragraph_control.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: PERFORM loop counts and sequential paragraphs.
- **Known Limitations**: Fall-through structures require paragraph index loops.

### GO TO
- **Parser Location**: [`modernize/parser.py:parse_goto_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L1105)
- **Semantic IR**: `STATEMENT` (statement_type="GOTO")
- **Generator Location**: [`modernize/native_generator.py:_translate_statement_inner`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: `nextParagraphIndex` pointer manipulation.
- **Test File(s)**: [`tests/test_phase8_control_flow.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_phase8_control_flow.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Simple GO TO targets.
- **Known Limitations**: Dynamic GO TO DEPENDING ON is unsupported.

### CALL and LINKAGE
- **Parser Location**: [`modernize/parser.py:parse_call_statement`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L1231)
- **Semantic IR**: `STATEMENT` (statement_type="CALL") with parameters list.
- **Generator Location**: [`modernize/native_generator.py:_generate_call_block`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py#L2626)
- **Java Runtime Helper**: `CobolRef` wrappers, `CicsProgramRegistry` for online CICS transactions.
- **Test File(s)**: [`tests/test_native_call_translation.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_native_call_translation.py), [`tests/test_dependencies.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_dependencies.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Static program targets, BY REFERENCE parameter updates.
- **Known Limitations**: BY CONTENT parameters are copied but lack structural isolation.

### Embedded SQL (DB2 / COMMIT / ROLLBACK)
- **Parser Location**: [`modernize/parser.py:parse_exec_sql`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L2611)
- **Semantic IR**: `STATEMENT` (statement_type="EXEC_SQL")
- **Generator Location**: [`modernize/native_generator.py:_translate_statement_inner`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: `SpringContextHelper.jdbcTemplate`
- **Test File(s)**: [`tests/test_db2_dialect_null_indicators.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_db2_dialect_null_indicators.py), [`tests/test_db2_acceptance.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_db2_acceptance.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: SELECT, INSERT, UPDATE, DELETE queries, Cursor open/fetch/close, COMMIT, and ROLLBACK. Null indicator host variables supported.
- **Known Limitations**: H2 is emulated. REAL_DB2 mode requires specific Docker configurations.

### CICS Commands
- **Parser Location**: [`modernize/parser.py:parse_exec_cics`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py#L2629)
- **Semantic IR**: `STATEMENT` (statement_type="EXEC_CICS")
- **Generator Location**: [`modernize/native_generator.py:_translate_statement_inner`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py)
- **Java Runtime Helper**: `CicsTransactionContext`, `CicsProgramRegistry`
- **Test File(s)**: [`tests/test_cics_modernization.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_cics_modernization.py), [`tests/test_cics_map_semantics.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_cics_map_semantics.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: SEND, RECEIVE, LINK, RETURN, XCTL commands.
- **Known Limitations**: Context maps mock terminal outputs.

### JCL steps
- **Parser Location**: [`modernize/jcl_parser.py:JclParser`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/jcl_parser.py)
- **Semantic IR**: JclJob model properties.
- **Generator Location**: [`modernize/jcl_generator.py:JclGenerator`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/jcl_generator.py)
- **Java Runtime Helper**: `JclExecutionContext`
- **Test File(s)**: [`tests/test_jcl_modernization.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tests/test_jcl_modernization.py)
- **Evidence Level**: `UNIT_TESTED`
- **Supported Subset**: Step return codes checking, step transition parameters.
- **Known Limitations**: Advanced JCL features (e.g. COND=ONLY/EVEN) are ignored or bypassed.

### IMS/DB and MQ calls
- **Parser Location**: None
- **Semantic IR**: None
- **Generator Location**: None
- **Java Runtime Helper**: None
- **Test File(s)**: None
- **Evidence Level**: `UNSUPPORTED`
- **Supported Subset**: None.
- **Known Limitations**: Completely unsupported in the current modernization pipeline.
