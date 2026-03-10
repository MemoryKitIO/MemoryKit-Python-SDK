# MemoryKit Python SDK

The official Python SDK for the [MemoryKit](https://memorykit.io) API — memory infrastructure for AI applications.

[![PyPI version](https://img.shields.io/pypi/v/memorykit.svg)](https://pypi.org/project/memorykit/)
[![Python versions](https://img.shields.io/pypi/pyversions/memorykit.svg)](https://pypi.org/project/memorykit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Installation

```bash
pip install memorykit
```

Requires Python 3.8+. The only runtime dependency is [httpx](https://www.python-httpx.org/).

## Quick Start

```python
from memorykit import MemoryKit

mk = MemoryKit(api_key="ctx_...")

# Create a memory
memory = mk.memories.create(
    content="Python was created by Guido van Rossum in 1991.",
    tags=["python", "history"],
    userId="user_123",
)
print(memory.id, memory.status)

# Search your knowledge base
results = mk.memories.search(query="Who created Python?", limit=5)
for result in results.results:
    print(result.id, result.score)
```

## Async Support

```python
from memorykit import AsyncMemoryKit

mk = AsyncMemoryKit(api_key="ctx_...")

memory = await mk.memories.create(content="...")
results = await mk.memories.search(query="...")
```

## Configuration

```python
mk = MemoryKit(
    api_key="ctx_...",
    base_url="https://api.memorykit.io/v1",  # default
    timeout=30.0,                              # seconds, default
    max_retries=3,                             # default, retries on 429 and 5xx
)
```

Both clients support context managers:

```python
with MemoryKit(api_key="ctx_...") as mk:
    mk.memories.create(content="...")

async with AsyncMemoryKit(api_key="ctx_...") as mk:
    await mk.memories.create(content="...")
```

## API Reference

### Memories

#### Create a memory

```python
memory = mk.memories.create(
    content="Meeting notes from Q4 planning...",
    title="Q4 Planning Notes",
    type="document",
    tags=["meetings", "planning"],
    metadata={"department": "engineering"},
    userId="user_123",
    language="en",
)
```

#### Batch create

```python
result = mk.memories.batch_create(
    items=[
        {"content": "First memory", "tags": ["batch"]},
        {"content": "Second memory", "tags": ["batch"]},
    ],
    defaults={"type": "note", "userId": "user_123"},
)
print(f"Accepted: {result.accepted}, Rejected: {result.rejected}")
```

#### Upload a file

```python
with open("report.pdf", "rb") as f:
    memory = mk.memories.upload(
        file=("report.pdf", f, "application/pdf"),
        title="Q4 Report",
        tags=["reports"],
        userId="user_123",
    )
```

#### List memories

```python
memories = mk.memories.list(limit=20, status="completed", userId="user_123")
for memory in memories:
    print(memory.id, memory.title)

# Pagination
if memories.has_more:
    next_page = mk.memories.list(cursor=memories.cursor)
```

#### Get a memory

```python
memory = mk.memories.get("mem_abc123")
print(memory.content)
```

#### Update a memory

```python
memory = mk.memories.update(
    "mem_abc123",
    title="Updated Title",
    tags=["updated"],
)
```

#### Reprocess a memory

```python
memory = mk.memories.reprocess("mem_abc123")
```

#### Delete a memory

```python
mk.memories.delete("mem_abc123")
```

#### Hybrid Search

```python
results = mk.memories.search(
    query="Q4 planning decisions",
    precision="high",
    limit=10,
    include_graph=True,
    tags=["meetings"],
    user_id="user_123",
    created_after="2025-01-01T00:00:00Z",
)
for result in results.results:
    print(result.id, result.score)
```

### Users

#### Create or update a user

```python
user = mk.users.upsert(
    id="user_123",
    name="Alice",
    email="alice@example.com",
    metadata={"plan": "pro"},
)
```

#### Get a user

```python
user = mk.users.get("user_123")
print(user.name, user.email)
```

#### Update a user

```python
user = mk.users.update("user_123", name="Alice Smith")
```

#### Delete a user

```python
mk.users.delete("user_123", cascade=True)
```

#### Create a user event

```python
event = mk.users.create_event(
    "user_123",
    type="page_view",
    data={"page": "/settings", "duration": 30},
)
```

#### List user events

```python
events = mk.users.list_events("user_123", limit=50, type="page_view")
for event in events:
    print(event.type, event.data)
```

#### Delete a user event

```python
mk.users.delete_event("user_123", "evt_abc123")
```

### Webhooks

#### Register a webhook

```python
webhook = mk.webhooks.create(
    url="https://example.com/webhook",
    events=["memory.completed", "memory.failed"],
)
print(webhook.id, webhook.secret)  # Save the secret for verification
```

#### List webhooks

```python
webhooks = mk.webhooks.list()
for wh in webhooks:
    print(wh.id, wh.url)
```

#### Get a webhook

```python
webhook = mk.webhooks.get("wh_abc123")
```

#### Test a webhook

```python
result = mk.webhooks.test("wh_abc123")
print(result.success, result.status_code)
```

#### Delete a webhook

```python
mk.webhooks.delete("wh_abc123")
```

### Status

```python
status = mk.status.get()
print(status.to_dict())
```

### Feedback

```python
feedback = mk.feedback.create(
    request_id="req_abc123",
    rating=5,
    comment="Very helpful answer",
)
```

## Parameter Naming

The MemoryKit API uses camelCase parameters (`userId`, `maxSources`, `includeGraph`). This SDK accepts **both** Python-style snake_case and camelCase:

```python
# Both of these work identically:
mk.memories.search(query="...", user_id="user_123", include_graph=True)
mk.memories.search(query="...", userId="user_123", includeGraph=True)
```

## Response Objects

All responses are typed objects with attribute access:

```python
results = mk.memories.search(query="...")
print(results.results)     # attribute access
print(results.total)
print(results["results"])  # dict-style access also works
print(results.to_dict())   # convert to plain dict
```

## Error Handling

```python
from memorykit import (
    MemoryKitError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

try:
    memory = mk.memories.get("mem_nonexistent")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except MemoryKitError as e:
    print(f"API error {e.status_code}: {e.message}")
    print(f"Error code: {e.code}")
    print(f"Request ID: {e.request_id}")
```

## Retry Behavior

The SDK automatically retries requests on HTTP 429 (rate limit) and 5xx (server errors) with exponential backoff and jitter. Configure with `max_retries`:

```python
mk = MemoryKit(api_key="ctx_...", max_retries=5)

# Disable retries
mk = MemoryKit(api_key="ctx_...", max_retries=0)
```

## Links

- [Documentation](https://docs.memorykit.io)
- [API Reference](https://docs.memorykit.io/api-reference)
- [Dashboard](https://platform.memorykit.io)
- [GitHub](https://github.com/MemoryKitIO/memorykit-python)

## License

MIT License. See [LICENSE](LICENSE) for details.
