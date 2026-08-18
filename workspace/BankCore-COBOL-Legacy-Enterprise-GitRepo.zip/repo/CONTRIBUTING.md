# Contributing

This repository is intentionally designed as a legacy modernization test fixture.

When modifying the application:

1. Preserve the business rules unless the test scenario explicitly changes them.
2. Keep source/copybook relationships intact.
3. Document intentional changes.
4. Run the GnuCOBOL build and runtime scripts before committing.
5. Keep modernization fixtures under `src/` or `docs/` clearly identified.
