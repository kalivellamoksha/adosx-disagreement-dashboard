# ADOSX — Engineering Decisions

## Decision 1: Use Django REST Framework

**Decision:** Use Django REST Framework for the backend API.

**Rejected alternative:** Implement all comparison logic in React.

**Reasoning:** Keeping reconciliation on the backend makes the comparison logic easier to test and prevents the frontend from directly processing the complete dataset.

## Decision 2: Use SQLite

**Decision:** Use SQLite as the database.

**Rejected alternative:** PostgreSQL.

**Reasoning:** The supplied dataset is small, and SQLite makes the application easier to run from a clean clone without extra database configuration.

## Decision 3: Preserve Original CSV Values

**Decision:** Store the original CSV fields alongside parsed numeric values.

**Rejected alternative:** Discard rows containing invalid values.

**Reasoning:** Invalid rows may be important disagreements, so preserving them prevents silent data loss.

## Decision 4: Normalize Record References

**Decision:** Normalize System B references before matching them with System A records.

**Rejected alternative:** Compare references exactly as written.

**Reasoning:** Different formatting should not cause the same record to appear missing.

## Decision 5: Use Decimal for Numeric Comparisons

**Decision:** Convert valid numeric values into Python Decimal values.

**Rejected alternative:** Use floating-point numbers.

**Reasoning:** Decimal provides more predictable comparisons for values representing monetary amounts.

## Decision 6: Use Server-Controlled Tenant Context

**Decision:** Restrict the API to a server-configured organization.

**Rejected alternative:** Allow the frontend to select any organization using a URL parameter.

**Reasoning:** The server should determine the accessible organization rather than trusting a client-provided tenant identifier.

## Decision 7: Keep the Dashboard Simple

**Decision:** Build a plain React table with filtering and sorting.

**Rejected alternative:** Spend additional time building an advanced dashboard interface.

**Reasoning:** The assignment emphasizes correctness, dirty-data handling, and tests over visual appearance.

## Decision 8: Prioritize Comparison Tests

**Decision:** Write focused automated tests for disagreement detection and tenant isolation.

**Rejected alternative:** Test every UI component before testing the comparison engine.

**Reasoning:** Reconciliation accuracy and tenant safety are the most important behaviors to protect against regressions.