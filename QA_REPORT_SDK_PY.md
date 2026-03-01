# QA Report: MemoryKit Python SDK v0.1.1

**Date**: 2026-02-26
**Scope**: `memorykit/` source + `tests/` against Backend (`/v1/` public API) and TypeScript SDK
**Verdict**: Shippable with known issues documented below

---

## 1. Lint Results

**Tool**: ruff (configured in `pyproject.toml`, target `py39`)

| Target | Result |
|--------|--------|
| `memorykit/` | All checks passed |
| `tests/` | All checks passed |

No lint issues found.

---

## 2. API Contract Mismatches

### 2.1 Endpoint Coverage

| Backend Endpoint | HTTP | Python SDK Method | Status |
|---|---|---|---|
| `POST /v1/memories` | 202 | `memories.create()` | OK |
| `POST /v1/memories/batch` | 202 | `memories.batch_create()` | OK |
| `POST /v1/memories/upload` | 202 | `memories.upload()` | OK |
| `GET /v1/memories` | 200 | `memories.list()` | OK |
| `GET /v1/memories/{id}` | 200 | `memories.get()` | OK |
| `PUT /v1/memories/{id}` | 200 | `memories.update()` | OK |
| `DELETE /v1/memories/{id}` | 204 | `memories.delete()` | OK |
| `POST /v1/memories/{id}/reprocess` | 202 | `memories.reprocess()` | OK |
| `POST /v1/memories/query` | 200 | `memories.query()` | OK |
| `POST /v1/memories/query` (stream=true) | SSE | `memories.stream()` | OK |
| `POST /v1/memories/search` | 200 | `memories.search()` | OK |
| `POST /v1/chats` | 201 | `chats.create()` | OK |
| `GET /v1/chats` | 200 | `chats.list()` | OK |
| `GET /v1/chats/{id}` | - | - | **NOT IN BACKEND** (see 2.2) |
| `POST /v1/chats/{id}/messages` | 200 | `chats.send_message()` | OK |
| `POST /v1/chats/{id}/messages/stream` | SSE | `chats.stream_message()` | OK |
| `GET /v1/chats/{id}/messages` | 200 | `chats.get_history()` | OK |
| `DELETE /v1/chats/{id}` | 204 | `chats.delete()` | OK |
| `POST /v1/users` | 200 | `users.upsert()` | OK |
| `GET /v1/users/{id}` | 200 | `users.get()` | OK |
| `PUT /v1/users/{id}` | 200 | `users.update()` | OK |
| `DELETE /v1/users/{id}` | 204 | `users.delete()` | OK |
| `POST /v1/users/{id}/events` | 201 | `users.create_event()` | OK |
| `GET /v1/users/{id}/events` | 200 | `users.list_events()` | OK |
| `DELETE /v1/users/{id}/events/{eid}` | 204 | `users.delete_event()` | OK |
| `POST /v1/webhooks` | 201 | `webhooks.create()` | OK |
| `GET /v1/webhooks` | 200 | `webhooks.list()` | OK |
| `GET /v1/webhooks/{id}` | 200 | `webhooks.get()` | OK |
| `DELETE /v1/webhooks/{id}` | 204 | `webhooks.delete()` | OK |
| `POST /v1/webhooks/{id}/test` | 200 | `webhooks.test()` | OK |
| `GET /v1/status` | 200 | `status.get()` | OK |
| `POST /v1/feedback` | 201 | `feedback.create()` | OK |

**Result**: 31/31 Backend endpoints are covered. No missing SDK methods.

### 2.2 CLAUDE.md Documents a Non-Existent Endpoint

The Python SDK `CLAUDE.md` documents `GET /v1/chats/:id` mapped to `mk.chats.get()`, but:
- The Backend does NOT have this endpoint
- The Python SDK does NOT implement this method
- The TS SDK does NOT implement this method either

**Severity**: Low (documentation error only; no code impact)
**Action**: Remove the `GET /v1/chats/:id` / `chats.get()` row from `CLAUDE.md`

### 2.3 CLAUDE.md Method Name Mismatch for Feedback

The Python SDK `CLAUDE.md` maps `POST /v1/feedback` to `mk.feedback.submit()`, but the actual implementation uses `mk.feedback.create()`. The TS SDK also uses `feedback.create()`.

**Severity**: Low (documentation error only)
**Action**: Update `CLAUDE.md` to say `mk.feedback.create()` instead of `mk.feedback.submit()`

### 2.4 Missing Query Parameters vs Backend

| Parameter | Backend Schema Field | Python SDK Method | Status |
|---|---|---|---|
| `model` | `QueryRequest.model` | `memories.query()` | **MISSING** |
| `history` | `QueryRequest.history` | `memories.query()` | **MISSING** |
| `score_threshold` | `QueryRequest.score_threshold` | `memories.query()` | **MISSING** |
| `stream` (explicit) | `QueryRequest.stream` | `memories.query()` | **MISSING** (only used internally by `stream()`) |
| `model` | `SendMessageRequest.model` | `chats.send_message()` | **MISSING** |
| `model` | `SendMessageRequest.model` | `chats.stream_message()` | **MISSING** |

**Severity**: Medium
- `model` parameter: Users cannot select the LLM model (gpt-5-nano, gpt-5-mini, gpt-4o-mini, gpt-4o) through the SDK. The TS SDK exposes this via `QueryParams.model` and `SendMessageParams.model`.
- `history` parameter: Users cannot pass conversation history for multi-turn queries through the SDK. The TS SDK exposes this via `QueryParams.history`.
- `score_threshold` on query: Backend accepts it on `/memories/query` but SDK only exposes it on `/memories/search`.

### 2.5 Streaming Path Inconsistency

The SDK `memories.stream()` sends `POST /memories/query` with `stream=true` in the body. This is correct -- the Backend uses the same endpoint with `stream` field toggling behavior. The TS SDK uses the same approach.

However, the `CLAUDE.md` in the Python SDK documents the streaming endpoint as `POST /v1/memories/query/stream` (a separate path), which does NOT exist in the Backend. The actual mechanism is `POST /v1/memories/query` with `{"stream": true}`.

**Severity**: Low (documentation inaccuracy; code is correct)

---

## 3. Type Safety Issues

### 3.1 Falsy-Value Bug in `or` Coalescing

**Severity**: HIGH -- behavioral bug

Multiple methods use `x or y` to merge snake_case and camelCase params. This fails when the snake_case value is falsy (e.g., `0`, `0.0`, `False`, `""`).

**Affected locations**:

| File | Line | Expression | Bug Trigger |
|---|---|---|---|
| `memories.py:63` | `user_id or userId` | `user_id=""` |
| `memories.py:274` | `max_sources or maxSources` | `max_sources=0` |
| `memories.py:279` | `response_format or responseFormat` | `response_format=""` |
| `memories.py:315` | `score_threshold or scoreThreshold` | `score_threshold=0.0` |
| `chats.py:41` | `user_id or userId` | `user_id=""` |
| `chats.py:135` | `max_sources or maxSources` | `max_sources=0` |
| `chats.py:139` | `response_format or responseFormat` | `response_format=""` |

**Fix**: Replace `x or y` with `x if x is not None else y` (the pattern already used for `include_graph`).

Example fix:
```python
# Before (buggy):
"max_sources": max_sources or maxSources,

# After (correct):
"max_sources": max_sources if max_sources is not None else maxSources,
```

### 3.2 Type Annotations Are Not Enforced at Runtime

The `_types.py` classes use class-level type annotations (e.g., `id: str`, `status: str`) on `APIObject` subclasses, but these are purely decorative. `APIObject.__getattr__` returns whatever is in `_data` dict with no validation. If the API returns `null` for a field annotated as `str`, no error is raised.

**Severity**: Low (standard pattern for dynamic SDKs, but users reading type hints may be misled)

### 3.3 `_parse_sse_line` Has Incorrect Return Type

In `_sse.py:14-22`, the function signature says `-> dict[str, Any] | None` but actually returns `str`. A `# type: ignore[return-value]` comment suppresses the error. This function is dead code -- it is never called in production, only tested for `None` returns in tests.

**Severity**: Low (dead code; no runtime impact)
**Action**: Remove `_parse_sse_line` or fix its return type and implementation.

### 3.4 `Feedback.rating` Typed as `Any`, Backend Requires `"positive" | "negative"`

In `_types.py:325`, `Feedback.rating` is typed `Any | None`. The Backend schema (`CreateFeedbackRequest.rating`) requires `pattern="^(positive|negative)$"`. Similarly, `FeedbackResource.create()` accepts `rating: Any`.

The TS SDK correctly types this as `rating: 'positive' | 'negative'`.

**Severity**: Medium (no runtime validation; users could pass invalid values)
**Action**: Change `rating` parameter type to `str` with a Literal hint, or at minimum document valid values.

### 3.5 Backend Response Fields Missing from SDK Types

| Backend Response | Field | Python SDK Type | Status |
|---|---|---|---|
| `MemoryResponse` | `chunks_count` | `Memory` | **MISSING** from class annotations |
| `MemoryResponse` | `format` | `Memory` | Present |
| `ChatResponse` | `message_count` | `Chat` | **MISSING** from class annotations |
| `WebhookResponse` | `is_active` | `Webhook` | **MISSING** from class annotations |
| `WebhookResponse` | `failure_count` | `Webhook` | **MISSING** from class annotations |
| `SearchResponse` | `processing_time_ms` | `SearchResponse` | **MISSING** from class annotations |

**Severity**: Low (fields are still accessible via `obj["field_name"]` or `obj.field_name` due to `APIObject` dynamic access, but IDE autocompletion won't show them)

---

## 4. SDK Parity Issues (Python vs TypeScript)

### 4.1 Feature Parity Matrix

| Feature | TypeScript SDK | Python SDK | Gap |
|---|---|---|---|
| Sync client | N/A (JS is async-only) | `MemoryKit` | N/A |
| Async client | `MemoryKit` | `AsyncMemoryKit` | OK |
| memories.create() | Yes | Yes | OK |
| memories.batchCreate() | Yes | Yes (`batch_create`) | OK |
| memories.upload() | Yes | Yes | OK |
| memories.list() | Yes | Yes | OK |
| memories.get() | Yes | Yes | OK |
| memories.update() | Yes | Yes | OK |
| memories.delete() | Yes | Yes | OK |
| memories.reprocess() | Yes | Yes | OK |
| memories.query() | Yes | Yes | OK |
| memories.search() | Yes | Yes | OK |
| memories.stream() | Yes | Yes | OK |
| `model` param on query | Yes | **NO** | **GAP** |
| `history` param on query | Yes | **NO** | **GAP** |
| chats.create() | Yes | Yes | OK |
| chats.list() | Yes | Yes | OK |
| chats.getHistory() | Yes | Yes (`get_history`) | OK |
| chats.sendMessage() | Yes | Yes (`send_message`) | OK |
| chats.streamMessage() | Yes | Yes (`stream_message`) | OK |
| chats.delete() | Yes | Yes | OK |
| `model` param on sendMessage | Yes | **NO** | **GAP** |
| users.upsert() | Yes | Yes | OK |
| users.get() | Yes | Yes | OK |
| users.update() | Yes | Yes | OK |
| users.delete() | Yes | Yes | OK |
| users.createEvent() | Yes | Yes (`create_event`) | OK |
| users.listEvents() | Yes | Yes (`list_events`) | OK |
| users.deleteEvent() | Yes | Yes (`delete_event`) | OK |
| webhooks.create() | Yes | Yes | OK |
| webhooks.list() | Yes | Yes | OK |
| webhooks.get() | Yes | Yes | OK |
| webhooks.delete() | Yes | Yes | OK |
| webhooks.test() | Yes | Yes | OK |
| status.get() | Yes | Yes | OK |
| feedback.create() | Yes | Yes | OK |

### 4.2 Error Class Parity

| Error Class | TypeScript | Python | Notes |
|---|---|---|---|
| MemoryKitError | Yes | Yes | OK |
| AuthenticationError | Yes (401) | Yes (401) | OK |
| PermissionError | Yes (403) | Yes (403) | OK |
| NotFoundError | Yes (404) | Yes (404) | OK |
| ValidationError | Yes (400/422) | Yes (400) | **Python does not handle 422** |
| RateLimitError | Yes (429) | Yes (429) | OK |
| ServerError | Yes (5xx) | Yes (5xx) | OK |
| ConnectionError | N/A | Yes | Python-only (httpx-specific) |
| TimeoutError | N/A | Yes | Python-only (httpx-specific) |

**Note**: Python SDK's `_raise_for_status` does not map HTTP 422 (Unprocessable Entity) to `ValidationError`. FastAPI commonly returns 422 for Pydantic validation failures. The TS SDK handles both 400 and 422 as ValidationError.

**Severity**: Medium
**Action**: Add `422: ValidationError` to `_STATUS_MAP` in `_errors.py`.

### 4.3 Key Conversion Architecture Difference

- **TS SDK**: Converts outgoing keys from camelCase to snake_case (via `toSnakeCase()`), and incoming keys from snake_case to camelCase (via `toCamelCase()`).
- **Python SDK**: Does NOT convert outgoing keys (sends snake_case as-is, which the Backend expects). Converts incoming keys from camelCase to snake_case (via `_convert_keys_to_snake()`).

This means the Python SDK's parameter names must match the Backend's snake_case convention. The dual `user_id`/`userId` parameters on methods are a convenience wrapper that coalesces before sending.

**Status**: Architecturally correct but different approach. No bug.

### 4.4 Webhook `list()` Return Type Difference

- **TS SDK**: `webhooks.list()` returns `Webhook[]` (plain array)
- **Python SDK**: `webhooks.list()` returns `WebhookList` (wrapper with `.data` list)

The Backend returns `{"data": [...]}` for webhook list. The Python SDK correctly wraps this in `WebhookList`, but the TS SDK unwraps it (or expects a raw array). This is an inconsistency between the two SDKs.

**Severity**: Low (both work, just different ergonomics)

### 4.5 Timeout Units

- **TS SDK**: `timeout` in milliseconds (default `30000`)
- **Python SDK**: `timeout` in seconds (default `30.0`)

This is documented but could surprise developers switching between SDKs.

**Severity**: Low (documented, language-idiomatic)

---

## 5. Test Results

```
171 passed in 0.65s
```

All 171 tests pass. Test breakdown:

| Test File | Count | Description |
|---|---|---|
| `test_exports.py` | ~15 | Verifies public API exports (`__all__`) |
| `test_sse.py` | ~10 | SSE parsing (event blocks, lines, edge cases) |
| `test_async_client.py` | ~10 | AsyncMemoryKit resource initialization |
| `test_endpoint_paths.py` | ~20 | Correct HTTP paths and methods per resource |
| `test_models.py` | ~20 | Type construction from dicts |
| `test_request_building.py` | ~30 | Request body/params construction |
| `test_client.py` | ~15 | SyncHTTPClient init, config, error handling |
| `test_return_types.py` | ~30 | Correct return type per method |

### 5.1 Test Coverage Gaps

The tests use mock/spy patterns to verify request construction but do NOT:
- Test actual HTTP round-trips (no pytest-httpx transport mocking)
- Test retry logic (backoff, retry-after header)
- Test streaming iteration end-to-end
- Test error deserialization from real API error bodies
- Test upload (multipart form-data) construction
- Test `_convert_keys_to_snake` / `_convert_keys_to_camel` round-trip fidelity

---

## 6. Bugs and Recommendations

### BUGS (must fix before next release)

| ID | Severity | Description | Location |
|---|---|---|---|
| BUG-1 | HIGH | Falsy-value coalescing: `x or y` fails for `0`, `0.0`, `""`, `False`. Use `x if x is not None else y`. | `memories.py` (6 sites), `chats.py` (4 sites) -- see Section 3.1 |
| BUG-2 | MEDIUM | HTTP 422 not mapped to `ValidationError`. FastAPI returns 422 for Pydantic failures. | `_errors.py:154` -- add `422: ValidationError` |
| BUG-3 | MEDIUM | Missing `model` param on `memories.query()`, `memories.stream()`, `chats.send_message()`, `chats.stream_message()`. Backend accepts it; TS SDK exposes it. | `memories.py`, `chats.py` |
| BUG-4 | MEDIUM | Missing `history` param on `memories.query()` and `memories.stream()`. Backend accepts it; TS SDK exposes it. | `memories.py` |

### RECOMMENDATIONS (improve quality)

| ID | Priority | Description |
|---|---|---|
| REC-1 | High | Add `score_threshold` parameter to `memories.query()` (Backend `QueryRequest` has it). |
| REC-2 | Medium | Add missing fields to type annotations: `Memory.chunks_count`, `Chat.message_count`, `Webhook.is_active`, `Webhook.failure_count`, `SearchResponse.processing_time_ms` for IDE autocompletion. |
| REC-3 | Medium | Type `Feedback.rating` as `Literal["positive", "negative"]` instead of `Any` to match Backend validation. |
| REC-4 | Medium | Remove dead code: `_parse_sse_line()` in `_sse.py` (never called in production, return type is wrong). |
| REC-5 | Medium | Fix `CLAUDE.md` documentation: remove `chats.get()`, rename `feedback.submit()` to `feedback.create()`, fix streaming path from `/memories/query/stream` to `/memories/query` with `stream=true`. |
| REC-6 | Low | Add integration tests using `pytest-httpx` for: retry logic, streaming iteration, error deserialization, upload multipart, key conversion round-trips. |
| REC-7 | Low | Consider validating `api_key` format (must start with `ctx_`) in client constructor, matching TS SDK behavior. Currently only checks for empty string. |
| REC-8 | Low | Add `py.typed` marker file for PEP 561 typed package support so mypy/pyright recognize the package as typed. |

---

## Summary

The Python SDK is functionally complete with all 31 Backend endpoints covered and 171 tests passing. The most critical issue is **BUG-1** (falsy-value coalescing with `or`), which silently drops valid parameter values like `max_sources=0` or `score_threshold=0.0`. The other medium-severity items (422 mapping, missing `model`/`history` params) affect feature completeness relative to the Backend and TS SDK.
