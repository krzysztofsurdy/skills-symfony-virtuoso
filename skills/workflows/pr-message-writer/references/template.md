# PR Message Template

Use this template as the structure for all pull request descriptions. Include or omit sections as appropriate for the change type.

---

## Title

```
[TICKET-ID] Short imperative description of the change
```

If no ticket ID is available, omit the prefix.

## Body

### What have I changed

Describe changes grouped by logical area. Use sub-headings or bullet points for clarity.

**Guidelines:**
- Group related file changes together (e.g., "Entity and Migration", "API Layer", "Admin Panel")
- Explain *why* each change was made, not just *what* changed
- Mention new dependencies, configuration changes, or environment variables
- Flag breaking changes prominently with a **BREAKING** prefix
- Note any changes that require cache clearing, queue restart, or deployment steps

#### Database and Entity/Model Changes
- New tables, columns, indexes, or foreign keys
- Migration file names and what they do
- Any data migrations or seed changes

#### API Changes (REST/GraphQL)
- New or modified endpoints, queries, or mutations
- Request/response schema changes
- Deprecations or removals

#### Admin Interface Changes
- New admin pages, list views, or form fields
- Filter or search additions
- Ordering or display changes

#### Caching and Performance
- New or modified cache keys
- Invalidation strategy changes
- Query optimization notes

#### Security and Permissions
- New role checks or permission gates
- Authentication flow changes
- Input validation additions

#### Event Handling
- New events, listeners, or subscribers
- Message queue changes
- Async processing additions

### Testing instructions

Step-by-step instructions for the reviewer to verify the changes manually.

**Format:**
1. Setup steps (environment, data prerequisites)
2. Action steps (what to click, what API calls to make)
3. Expected results (what the reviewer should see)

#### API/Query examples

Provide copy-pasteable requests. Use generic staging URLs:

```graphql
# Example GraphQL mutation
mutation {
  createReview(input: { productId: "abc-123", rating: 5, comment: "Great product" }) {
    id
    status
  }
}
```

```bash
# Example REST call
curl -X POST https://your-staging.example.com/api/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "abc-123", "rating": 5, "comment": "Great product"}'
```

### Test scenarios

List specific scenarios that should be tested:

- [ ] Happy path: normal usage works as expected
- [ ] Edge case: boundary conditions are handled
- [ ] Error case: invalid input returns appropriate errors
- [ ] Permissions: unauthorized users are rejected
- [ ] Regression: existing functionality is not broken

### Database verification

SQL queries to confirm data integrity after testing:

```sql
-- Verify new records were created
SELECT id, status, created_at FROM your_table ORDER BY created_at DESC LIMIT 5;

-- Verify no orphaned records
SELECT COUNT(*) FROM child_table c
LEFT JOIN parent_table p ON c.parent_id = p.id
WHERE p.id IS NULL;
```

### Product changes

If the PR affects user-facing behavior, describe:
- What changes the end user will see
- Screenshots or screen recordings if applicable
- Any feature flags controlling the rollout
- Rollback plan if issues are discovered
