# Example PR Messages

Real-world examples demonstrating the PR template applied to different change types.

---

## Example 1: Feature — Add Product Review System

### Title
```
SHOP-1042 Add product review system with ratings and moderation
```

### What have I changed

#### Database and Entity/Model Changes

**New `ProductReview` entity:** `id` (UUID), `product_id` (FK), `user_id` (FK), `rating` (int 1-5), `comment` (text, nullable), `status` (enum: pending/approved/rejected), timestamps.

**Migration `Version20260215120000`** creates `product_review` table with unique constraint on `(product_id, user_id)` and index on `(product_id, status)`.

#### API Changes (REST/GraphQL)

**New `submitReview` mutation** — authenticated users submit a review for a purchased product. Validates purchase history, duplicate prevention, and rating range.

**New `productReviews` query** — paginated approved reviews with `averageRating` computed field. Updated `product` query includes `averageRating` and `reviewCount`.

#### Caching and Performance

Cache key `product_avg_rating:{productId}` with 1-hour TTL, invalidated on admin approve/reject. Cursor-based pagination on reviews query.

#### Admin Interface Changes

New "Product Reviews" admin page: list with filters (status, rating range), bulk approve/reject, detail view with moderation buttons.

### Testing instructions

```graphql
mutation {
  submitReview(input: { productId: "prod-001", rating: 5, comment: "Excellent quality." }) {
    review { id, status, rating }
    errors { field, message }
  }
}
```
**Expected:** Review created with `pending` status.

```graphql
query {
  productReviews(productId: "prod-001", first: 10) {
    edges { node { id, rating, comment, createdAt } }
    averageRating
    totalCount
  }
}
```
**Expected:** Only approved reviews returned, correct average.

**Admin approval:** Navigate to `https://your-staging.example.com/admin/product-reviews`, filter pending, approve a review, verify it appears in API.

**Duplicate prevention:** Submit a second review for the same product/user. Expected: validation error.

### Database verification

```sql
SELECT pr.id, pr.rating, pr.status, p.name, u.email
FROM product_review pr
JOIN product p ON pr.product_id = p.id
JOIN "user" u ON pr.user_id = u.id
ORDER BY pr.created_at DESC LIMIT 5;

SELECT p.id, ROUND(AVG(pr.rating), 2) AS avg_rating, COUNT(pr.id) AS cnt
FROM product p
LEFT JOIN product_review pr ON pr.product_id = p.id AND pr.status = 'approved'
GROUP BY p.id HAVING COUNT(pr.id) > 0 LIMIT 10;
```

### Product changes
- Users can leave 1-5 star reviews on purchased products
- Reviews require admin approval before becoming visible
- Product pages show average rating and review count

---

## Example 2: Bug Fix — Cart Quantity Not Preserved on Validation Error

### Title
```
SHOP-987 Fix cart quantity reset when validation fails on checkout
```

### What have I changed

#### Root Cause

`CartService::validateAndUpdate()` cleared cart items *before* validation. If validation failed, original quantities were lost.

#### Fix

Reordered to validate first, persist second:

**Before:** Clear items -> Insert updated -> Validate -> Rollback (quantities lost)
**After:** Validate -> If error, return (cart untouched) -> Clear items -> Insert updated

**Files changed:**
- `src/Service/CartService.php` — reordered validation and deletion
- `src/Validator/StockAvailabilityValidator.php` — extracted standalone validation
- `tests/Unit/Service/CartServiceTest.php` — quantity preservation test
- `tests/Integration/Cart/CartUpdateTest.php` — full checkout flow test

### Testing instructions

1. Add product to cart with quantity 2
2. Change quantity to 9999 (exceeds stock), submit
3. **Expected:** Validation error shown, quantity still 2

```graphql
mutation {
  updateCartItem(input: { cartItemId: "item-001", quantity: 9999 }) {
    cart { items { id, quantity } }
    errors { field, message }
  }
}
```
**Expected:** Error returned, `cart.items` shows original quantity.

**Edge cases:** quantity 0 (removes item), negative (validation error), exact stock limit (succeeds), multi-item with one invalid (all retain original).

### Test scenarios
- [x] `CartServiceTest::testQuantityPreservedOnValidationError`
- [x] `CartUpdateTest::testFullCheckoutFlowWithInvalidQuantity`
- [ ] Manual: browser verification

### Product changes
- Cart quantities no longer reset on validation errors during checkout

---

## Example 3: Feature — Add Quiz Question Pool with Admin Management

### Title
```
EDU-2103 Add quiz question pool system with admin CRUD and ordering
```

### What have I changed

#### Database and Entity/Model Changes

**New `QuizPool` entity:** `id`, `name` (unique), `description`, `is_active`, timestamps.

**New `QuizQuestion` entity:** `id`, `question_text`, `question_type` (multiple_choice/true_false/free_text), `difficulty` (easy/medium/hard), `options` (JSON), `correct_answer`, timestamps.

**New `QuizQuestionPool` join entity:** `quiz_pool_id` (FK), `quiz_question_id` (FK), `position` (int for ordering). Unique constraint on `(quiz_pool_id, quiz_question_id)`.

**Migration `Version20260220090000`** creates all three tables.

#### Admin Interface Changes

**Quiz Pools list:** name, question count, active status, date. Filters: active/inactive, date range.

**Create/Edit form:** name (required, unique), description, active toggle, question assignment panel with search-and-select, drag-and-drop reordering, duplicate prevention (assigned questions grayed out).

**QuizQuestion admin:** list with type/difficulty/pool count, dynamic options field for multiple choice, question preview.

#### Event Handling

`QuizPoolQuestionAddedEvent` and `QuizPoolQuestionRemovedEvent` dispatched on changes. Listener updates pool `updated_at`.

### Testing instructions

1. Navigate to `https://your-staging.example.com/admin/quiz-pools`, create pool "JavaScript Fundamentals"
2. Add questions via search panel, reorder with drag-and-drop, save
3. **Expected:** Questions saved with correct positions
4. Search for already-assigned question — should appear grayed out
5. Reload page — ordering persists

### Database verification

```sql
SELECT id, name, is_active FROM quiz_pool ORDER BY created_at DESC LIMIT 5;

SELECT qp.name, qq.question_text, qqp.position
FROM quiz_question_pool qqp
JOIN quiz_pool qp ON qqp.quiz_pool_id = qp.id
JOIN quiz_question qq ON qqp.quiz_question_id = qq.id
WHERE qp.name = 'JavaScript Fundamentals'
ORDER BY qqp.position ASC;

-- Verify no duplicates
SELECT quiz_pool_id, quiz_question_id, COUNT(*) FROM quiz_question_pool
GROUP BY quiz_pool_id, quiz_question_id HAVING COUNT(*) > 1;
```

### Product changes
- Administrators can organize questions into named, ordered pools
- Questions can be shared across pools
- Foundation for quiz/assessment delivery feature

---

## Example 4: Feature — Add User Preference Tracking Field

### Title
```
USR-455 Add notification_preference field to user profile
```

### What have I changed

#### Database and Entity/Model Changes

**Updated `User` entity** with `notification_preference` (enum: all/important_only/none, nullable). Default `NULL` means unset. Can be updated but not cleared back to `NULL`.

**Migration `Version20260222140000`:**
```sql
ALTER TABLE "user" ADD COLUMN notification_preference VARCHAR(20) DEFAULT NULL;
```

#### API Changes (REST/GraphQL)

**New `setNotificationPreference` mutation** — requires auth, accepts `ALL`/`IMPORTANT_ONLY`/`NONE`, returns updated profile. Users can only set their own preference.

**Updated `me` query** — includes `notificationPreference` (null if unset).

#### Security and Permissions

Auth check ensures user matches target. Admins can set any user's preference via `adminSetNotificationPreference`. Rate limited to 10 calls/minute/user.

### Testing instructions

```graphql
mutation {
  setNotificationPreference(input: { preference: IMPORTANT_ONLY }) {
    user { id, email, notificationPreference }
    errors { field, message }
  }
}
```
**Expected:** Returns user with `notificationPreference: "IMPORTANT_ONLY"`.

**Verify in profile:** `query { me { id, notificationPreference } }` — returns set value.

**Auth test:** Run mutation without auth token. Expected: 401 error.

**Invalid value:** Use `preference: INVALID_VALUE`. Expected: validation error.

**Admin override:**
```graphql
mutation {
  adminSetNotificationPreference(input: { userId: "user-042", preference: NONE }) {
    user { id, notificationPreference }
  }
}
```
Expected: succeeds for admin, permission error for non-admin.

### Database verification

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user' AND column_name = 'notification_preference';

SELECT id, email, notification_preference FROM "user"
WHERE notification_preference IS NOT NULL ORDER BY updated_at DESC LIMIT 10;

SELECT notification_preference, COUNT(*) FROM "user"
GROUP BY notification_preference ORDER BY COUNT(*) DESC;
```

### Product changes
- Users can set notification preference from profile settings
- Default is unset until user makes explicit choice
- Admins can override via admin panel
