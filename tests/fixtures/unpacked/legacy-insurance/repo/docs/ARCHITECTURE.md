# Architecture

```text
                +----------------------+
                | CICS Online Programs |
                +----------+-----------+
                           |
                           v
+-------------+     +------+-------+     +-------------+
| BMS Maps    | --> | COBOL Rules  | --> | DB2         |
+-------------+     +------+-------+     +-------------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
       +-----------+               +-----------+
       | VSAM KSDS |               | Sequential|
       +-----------+               | Files     |
                                   +-----------+

JCL -> Batch COBOL -> validation -> DB2 -> payment -> reports
```

The application is intentionally modular so a modernization engine can build a program/call/dependency graph and map legacy concerns into Java/Spring components.
