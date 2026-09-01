---
name: cobol-analysis
description: Analyzes raw COBOL-85 and IBM Enterprise COBOL source code for dialects, division structures, statements, and embedded EXEC SQL/CICS blocks.
---

# COBOL Analysis Skill

This skill provides step-by-step instructions for inspecting legacy mainframe COBOL programs.

## Analysis Workflow

1. **Dialect & Format Detection**:
   - Determine column layout: Fixed-format (columns 1-6 sequence, col 7 indicator, cols 8-72 Area A/B) vs Free-format.
   - Inspect Indicator Column (Column 7): `*` / `/` for comments, `-` for line continuation, `D` for debug lines.

2. **Division Inspection**:
   - `IDENTIFICATION DIVISION`: Extract `PROGRAM-ID`.
   - `ENVIRONMENT DIVISION`: Extract `INPUT-OUTPUT SECTION` and `SELECT ... ASSIGN` file mappings.
   - `DATA DIVISION`:
     - `FILE SECTION`: `FD` file descriptors.
     - `WORKING-STORAGE SECTION`: Variable records (`01`, `05`, `77`, `88`).
     - `LINKAGE SECTION`: Subroutine call arguments and CICS `DFHCOMMAREA`.
   - `PROCEDURE DIVISION`: Entry points, `USING` parameters, sections, paragraphs, statements.

3. **Embedded Subsystems**:
   - `EXEC SQL ... END-EXEC`: Identify host variables, cursors, queries, and DDL/DML operations.
   - `EXEC CICS ... END-EXEC`: Identify transactions, maps (`SEND MAP`, `RECEIVE MAP`), and program links (`LINK`, `XCTL`).
