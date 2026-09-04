# Business Rules

| ID | Rule |
|---|---|
| BR-001 | Policy must be ACTIVE for a normal claim. |
| BR-002 | Approved amount is capped at coverage limit. |
| BR-003 | Deductible is subtracted after coverage capping. |
| BR-004 | Net payment cannot be negative. |
| BR-005 | Approved amount > 200000 requires MANUAL_REVIEW. |
| BR-006 | Duplicate claim IDs are rejected. |
| BR-007 | Missing customer/policy rejects the transaction. |
| BR-008 | Every state transition produces an audit event. |
