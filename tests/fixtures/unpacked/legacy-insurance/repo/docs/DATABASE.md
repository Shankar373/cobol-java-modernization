# DB2 Design

Tables:

- CUSTOMER
- POLICY
- CLAIM
- PAYMENT
- CLAIM_HISTORY
- AUDIT_LOG

The schema uses primary keys, foreign keys, DECIMAL amounts, DATE fields and nullable attributes.

The SQL is intentionally written as legacy-style EXEC SQL source and is also represented in `db2/schema.sql`.
