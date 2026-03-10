# MemoryKit Python SDK

Official Python SDK for MemoryKit RAG API. Sync + Async clients, httpx-based, Python 3.8+.

## Quick Commands
```bash
pip install -e ".[dev]"        # Install with dev deps
python -c "import memorykit"   # Verify import
pytest                         # Run tests (when available)
mypy memorykit                 # Type checking
ruff check memorykit           # Linting
ruff format memorykit          # Formatting
```

## Architecture

```
memorykit/
├── __init__.py       # Public API exports (MemoryKit, AsyncMemoryKit, all types)
├── _client.py        # SyncHTTPClient + AsyncHTTPClient (httpx wrappers with retry)
├── _errors.py        # Error hierarchy (MemoryKitError → Auth/RateLimit/NotFound/etc.)
├── _types.py         # Dataclasses for all API types (Memory, Chat, User, etc.)
├── _sse.py           # SSE parser for streaming responses
├── memories.py       # Memories + AsyncMemories resource classes
├── chats.py          # Chats + AsyncChats resource classes
├── users.py          # Users + AsyncUsers resource classes (+ events)
├── webhooks.py       # Webhooks + AsyncWebhooks resource classes
├── feedback.py       # FeedbackResource + AsyncFeedbackResource
└── status.py         # StatusResource + AsyncStatusResource
```

## Conventions

- **Dual client pattern**: Every resource has sync (`Memories`) and async (`AsyncMemories`) versions
- **`MemoryKit`** = sync client, **`AsyncMemoryKit`** = async client
- **Snake_case throughout**: Python-native naming, httpx handles JSON key conversion
- **Dataclasses for types**: All API models in `_types.py` as `@dataclass` with `from_dict()` factory
- **Private modules**: Internal modules prefixed with `_` (`_client.py`, `_errors.py`, `_types.py`, `_sse.py`)
- **httpx dependency**: Only runtime dependency, handles HTTP/2, timeouts, retries
- **Streaming**: `_sse.py` yields `SSEEvent` objects from httpx byte streams

## API → SDK Method Mapping

| API Endpoint | Sync | Async |
|---|---|---|
| `POST /v1/memories` | `mk.memories.create()` | `await mk.memories.create()` |
| `GET /v1/memories` | `mk.memories.list()` | `await mk.memories.list()` |
| `GET /v1/memories/:id` | `mk.memories.get()` | `await mk.memories.get()` |
| `PUT /v1/memories/:id` | `mk.memories.update()` | `await mk.memories.update()` |
| `DELETE /v1/memories/:id` | `mk.memories.delete()` | `await mk.memories.delete()` |
| `GET /v1/memories/search` | `mk.memories.search()` | `await mk.memories.search()` |
| `POST /v1/memories/query` | `mk.memories.query()` | `await mk.memories.query()` |
| `POST /v1/memories/query/stream` | `mk.memories.stream()` | `async for event in mk.memories.stream()` |
| `POST /v1/memories/upload` | `mk.memories.upload()` | `await mk.memories.upload()` |
| `POST /v1/memories/:id/reprocess` | `mk.memories.reprocess()` | `await mk.memories.reprocess()` |
| `POST /v1/chats` | `mk.chats.create()` | `await mk.chats.create()` |
| `GET /v1/chats` | `mk.chats.list()` | `await mk.chats.list()` |
| `GET /v1/chats/:id` | `mk.chats.get()` | `await mk.chats.get()` |
| `DELETE /v1/chats/:id` | `mk.chats.delete()` | `await mk.chats.delete()` |
| `POST /v1/chats/:id/messages` | `mk.chats.send_message()` | `await mk.chats.send_message()` |
| `POST /v1/chats/:id/messages/stream` | `mk.chats.stream_message()` | `async for event in mk.chats.stream_message()` |
| `GET /v1/chats/:id/history` | `mk.chats.get_history()` | `await mk.chats.get_history()` |
| `POST /v1/users` | `mk.users.upsert()` | `await mk.users.upsert()` |
| `GET /v1/users/:id` | `mk.users.get()` | `await mk.users.get()` |
| `PUT /v1/users/:id` | `mk.users.update()` | `await mk.users.update()` |
| `DELETE /v1/users/:id` | `mk.users.delete()` | `await mk.users.delete()` |
| `POST /v1/users/:id/events` | `mk.users.create_event()` | `await mk.users.create_event()` |
| `GET /v1/users/:id/events` | `mk.users.list_events()` | `await mk.users.list_events()` |
| `DELETE /v1/users/:id/events/:eid` | `mk.users.delete_event()` | `await mk.users.delete_event()` |
| `POST /v1/webhooks` | `mk.webhooks.create()` | `await mk.webhooks.create()` |
| `GET /v1/webhooks` | `mk.webhooks.list()` | `await mk.webhooks.list()` |
| `GET /v1/webhooks/:id` | `mk.webhooks.get()` | `await mk.webhooks.get()` |
| `DELETE /v1/webhooks/:id` | `mk.webhooks.delete()` | `await mk.webhooks.delete()` |
| `POST /v1/webhooks/:id/test` | `mk.webhooks.test()` | `await mk.webhooks.test()` |
| `GET /v1/status` | `mk.status.get()` | `await mk.status.get()` |
| `POST /v1/feedback` | `mk.feedback.submit()` | `await mk.feedback.submit()` |

## Adding a New Method

1. Add dataclass types to `_types.py`
2. Add method to both sync and async resource classes
3. Export new types from `__init__.py`
4. Run `mypy memorykit` + `ruff check memorykit`
5. Update README.md

## Testing (TODO)

Currently 0% test coverage. Dev deps configured: pytest, pytest-asyncio, pytest-httpx.
Run `pip install -e ".[dev]"` to install test dependencies.
