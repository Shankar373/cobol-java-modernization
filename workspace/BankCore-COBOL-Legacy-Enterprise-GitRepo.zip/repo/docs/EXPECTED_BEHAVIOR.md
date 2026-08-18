# Expected Runtime Behavior

The supplied transaction file contains 8 transactions.

Expected result:

- 5 transactions should be posted
- 3 transactions should be rejected
- Posted credit count: 2
- Posted debit count: 1
- Posted transfer count: 2

Rejected cases intentionally cover:

1. overdraft/insufficient funds
2. missing account
3. unsupported transaction type

The important modernization acceptance criteria are behavioral equivalence,
not only successful compilation.
