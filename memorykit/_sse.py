"""Server-Sent Events (SSE) parser for MemoryKit streaming endpoints.

Supports both sync iteration (over ``httpx.Response``) and async iteration
(over ``httpx.Response`` from ``AsyncClient``).
"""

from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, Iterator, Optional


def _parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single SSE line pair into an event dict.

    Returns ``None`` if the line is a comment, keep-alive, or incomplete.
    """
    line = line.strip()
    if not line or line.startswith(":"):
        return None
    return line  # type: ignore[return-value]


def _parse_event_block(block: str) -> Optional[Dict[str, Any]]:
    """Parse a full SSE event block (separated by double newlines).

    Returns a dict with ``event`` and ``data`` keys, or ``None`` for empty blocks.
    """
    event_type: Optional[str] = None
    data_lines: list[str] = []

    for line in block.split("\n"):
        line = line.strip()
        if not line or line.startswith(":"):
            continue
        if line.startswith("event:"):
            event_type = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data_lines.append(line[len("data:"):].strip())

    if not data_lines:
        return None

    raw_data = "\n".join(data_lines)

    # Try parsing as JSON; fall back to raw string
    try:
        parsed_data = json.loads(raw_data)
    except (json.JSONDecodeError, ValueError):
        parsed_data = raw_data

    return {
        "event": event_type or "message",
        "data": parsed_data,
    }


class SSEIterator:
    """Synchronous iterator over SSE events from an ``httpx.Response`` stream."""

    def __init__(self, response: Any) -> None:
        self._response = response
        self._buffer = ""

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self._iterate()

    def _iterate(self) -> Iterator[Dict[str, Any]]:
        try:
            for chunk in self._response.iter_text():
                self._buffer += chunk
                # Split on double newlines (SSE event boundaries)
                while "\n\n" in self._buffer:
                    block, self._buffer = self._buffer.split("\n\n", 1)
                    event = _parse_event_block(block)
                    if event is not None:
                        yield event
                        if event["event"] == "done":
                            return

            # Handle any remaining data in the buffer
            if self._buffer.strip():
                event = _parse_event_block(self._buffer)
                if event is not None:
                    yield event
        finally:
            self._response.close()

    def close(self) -> None:
        """Close the underlying response stream."""
        self._response.close()


class AsyncSSEIterator:
    """Asynchronous iterator over SSE events from an ``httpx.Response`` stream."""

    def __init__(self, response: Any) -> None:
        self._response = response
        self._buffer = ""

    def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[Dict[str, Any]]:
        try:
            async for chunk in self._response.aiter_text():
                self._buffer += chunk
                while "\n\n" in self._buffer:
                    block, self._buffer = self._buffer.split("\n\n", 1)
                    event = _parse_event_block(block)
                    if event is not None:
                        yield event
                        if event["event"] == "done":
                            return

            if self._buffer.strip():
                event = _parse_event_block(self._buffer)
                if event is not None:
                    yield event
        finally:
            await self._response.aclose()

    async def aclose(self) -> None:
        """Close the underlying response stream."""
        await self._response.aclose()
