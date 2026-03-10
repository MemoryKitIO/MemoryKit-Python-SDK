"""Memories resource — create, query, search, and manage memory records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Union

from ._client import AsyncHTTPClient, SyncHTTPClient
from ._sse import AsyncSSEIterator, SSEIterator
from ._types import (
    BatchIngestResponse,
    Memory,
    MemoryList,
    # V2: query endpoint disabled for initial launch
    # QueryResponse,
    SearchResponse,
)


class Memories:
    """Synchronous interface for the Memories API.

    Access via ``mk.memories``.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def create(
        self,
        content: str,
        *,
        title: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        language: Optional[str] = None,
        format: Optional[str] = None,
    ) -> Memory:
        """Create a new memory.

        Args:
            content: The memory content (required).
            title: Optional title.
            type: Memory type.
            tags: List of tags.
            metadata: Arbitrary metadata dict.
            user_id: User ID to associate (snake_case form).
            userId: User ID to associate (camelCase form).
            language: Content language.
            format: Content format.

        Returns:
            The created :class:`Memory` object (status may be ``"processing"``).
        """
        body: Dict[str, Any] = {
            "content": content,
            "title": title,
            "type": type,
            "tags": tags,
            "metadata": metadata,
            "user_id": user_id or userId,
            "language": language,
            "format": format,
        }
        data = self._client.request("POST", "/memories", json=body)
        return Memory(data)

    def batch_create(
        self,
        items: List[Dict[str, Any]],
        *,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> BatchIngestResponse:
        """Batch ingest up to 100 memories.

        Args:
            items: List of memory objects (each must contain ``content``).
            defaults: Default values applied to all items.

        Returns:
            A :class:`BatchIngestResponse` with accepted/rejected counts.
        """
        body: Dict[str, Any] = {"items": items}
        if defaults is not None:
            body["defaults"] = defaults
        data = self._client.request("POST", "/memories/batch", json=body)
        return BatchIngestResponse(data)

    def upload(
        self,
        file: Any,
        *,
        title: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[str] = None,
        language: Optional[str] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Memory:
        """Upload a file as a memory (multipart/form-data).

        Args:
            file: A file-like object, or a tuple of ``(filename, file_obj)``
                  or ``(filename, file_obj, content_type)``.
            title: Optional title.
            type: Memory type.
            tags: Comma-separated tags or list (converted to comma-separated).
            metadata: JSON-serialised metadata string.
            language: Content language.
            user_id: User ID (snake_case).
            userId: User ID (camelCase).

        Returns:
            The created :class:`Memory` object.
        """
        if isinstance(file, tuple):
            files = {"file": file}
        else:
            files = {"file": file}

        form_data: Dict[str, Any] = {}
        if title is not None:
            form_data["title"] = title
        if type is not None:
            form_data["type"] = type
        if tags is not None:
            form_data["tags"] = ",".join(tags) if isinstance(tags, list) else tags
        if metadata is not None:
            form_data["metadata"] = metadata
        if language is not None:
            form_data["language"] = language

        uid = user_id or userId
        if uid is not None:
            form_data["userId"] = uid

        data = self._client.request("POST", "/memories/upload", files=files, data=form_data)
        return Memory(data)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> MemoryList:
        """List memories with cursor-based pagination.

        Args:
            limit: Maximum number of results (default 20).
            cursor: Pagination cursor from a previous response.
            status: Filter by status (e.g. ``"completed"``).
            type: Filter by memory type.
            user_id: Filter by user ID (snake_case).
            userId: Filter by user ID (camelCase).

        Returns:
            A :class:`MemoryList` with ``data``, ``has_more``, and ``cursor``.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "cursor": cursor,
            "status": status,
            "type": type,
            "user_id": user_id or userId,
        }
        data = self._client.request("GET", "/memories", params=params)
        return MemoryList(data)

    def get(self, memory_id: str) -> Memory:
        """Get a single memory by ID.

        Args:
            memory_id: The memory ID (e.g. ``"mem_abc123"``).

        Returns:
            The full :class:`Memory` object.
        """
        data = self._client.request("GET", f"/memories/{memory_id}")
        return Memory(data)

    def update(
        self,
        memory_id: str,
        *,
        title: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[str] = None,
    ) -> Memory:
        """Update an existing memory.

        Args:
            memory_id: The memory ID.
            title: New title.
            type: New type.
            tags: New tags.
            metadata: New metadata.
            content: New content.

        Returns:
            The updated :class:`Memory` object.
        """
        body: Dict[str, Any] = {
            "title": title,
            "type": type,
            "tags": tags,
            "metadata": metadata,
            "content": content,
        }
        data = self._client.request("PUT", f"/memories/{memory_id}", json=body)
        return Memory(data)

    def reprocess(self, memory_id: str) -> Memory:
        """Reprocess an existing memory.

        Args:
            memory_id: The memory ID.

        Returns:
            The :class:`Memory` object (status will be ``"processing"``).
        """
        data = self._client.request("POST", f"/memories/{memory_id}/reprocess")
        return Memory(data)

    def delete(self, memory_id: str) -> None:
        """Soft-delete a memory.

        Args:
            memory_id: The memory ID.
        """
        self._client.request("DELETE", f"/memories/{memory_id}")

    # V2: query endpoint disabled for initial launch
    # def query(
    #     self,
    #     query: str,
    #     *,
    #     max_sources: Optional[int] = None,
    #     maxSources: Optional[int] = None,
    #     temperature: Optional[float] = None,
    #     mode: Optional[str] = None,
    #     user_id: Optional[str] = None,
    #     userId: Optional[str] = None,
    #     instructions: Optional[str] = None,
    #     response_format: Optional[str] = None,
    #     responseFormat: Optional[str] = None,
    #     include_graph: Optional[bool] = None,
    #     includeGraph: Optional[bool] = None,
    #     filters: Optional[Dict[str, Any]] = None,
    # ) -> QueryResponse:
    #     body: Dict[str, Any] = {
    #         "query": query,
    #         "max_sources": max_sources or maxSources,
    #         "temperature": temperature,
    #         "mode": mode,
    #         "user_id": user_id or userId,
    #         "instructions": instructions,
    #         "response_format": response_format or responseFormat,
    #         "include_graph": include_graph if include_graph is not None else includeGraph,
    #         "filters": filters,
    #     }
    #     data = self._client.request("POST", "/memories/query", json=body)
    #     return QueryResponse(data)

    def search(
        self,
        query: str,
        *,
        precision: Optional[str] = None,
        limit: Optional[int] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[Union[List[str], str]] = None,
        created_after: Optional[Union[str, datetime]] = None,
        created_before: Optional[Union[str, datetime]] = None,
        include_graph: Optional[bool] = None,
        includeGraph: Optional[bool] = None,
    ) -> SearchResponse:
        """Perform a hybrid search across memories.

        Args:
            query: The search query (required).
            precision: Result precision level — ``"low"``, ``"medium"``
                (default), or ``"high"``.
            limit: Maximum results, 1-100 (default 10).
            user_id: Scope to a specific user (snake_case form).
            userId: Scope to a specific user (camelCase form).
            type: Filter by memory type.
            tags: Filter by tags. Accepts a list of strings (joined with
                comma) or a pre-joined comma-separated string.
            created_after: Only return memories created after this timestamp.
                Accepts an ISO 8601 string or a :class:`~datetime.datetime`
                object (converted via ``.isoformat()``).
            created_before: Only return memories created before this timestamp.
                Same formats as *created_after*.
            include_graph: Include knowledge graph data.

        Returns:
            A :class:`SearchResponse` with ``results``, ``graph``,
            ``total_results``.
        """
        # Normalise tags to comma-separated string
        if isinstance(tags, list):
            tags = ",".join(tags)

        # Normalise datetime objects to ISO 8601 strings
        if isinstance(created_after, datetime):
            created_after = created_after.isoformat()
        if isinstance(created_before, datetime):
            created_before = created_before.isoformat()

        params: Dict[str, Any] = {
            "query": query,
            "precision": precision,
            "limit": limit,
            "user_id": user_id or userId,
            "type": type,
            "tags": tags,
            "created_after": created_after,
            "created_before": created_before,
            "include_graph": include_graph if include_graph is not None else includeGraph,
        }
        data = self._client.request("GET", "/memories/search", params=params)
        return SearchResponse(data)

    # V2: streaming disabled for initial launch
    # def stream(
    #     self,
    #     query: str,
    #     *,
    #     max_sources: Optional[int] = None,
    #     maxSources: Optional[int] = None,
    #     temperature: Optional[float] = None,
    #     mode: Optional[str] = None,
    #     user_id: Optional[str] = None,
    #     userId: Optional[str] = None,
    #     instructions: Optional[str] = None,
    #     response_format: Optional[str] = None,
    #     responseFormat: Optional[str] = None,
    #     include_graph: Optional[bool] = None,
    #     includeGraph: Optional[bool] = None,
    #     filters: Optional[Dict[str, Any]] = None,
    # ) -> SSEIterator:
    #     body: Dict[str, Any] = {
    #         "query": query,
    #         "max_sources": max_sources or maxSources,
    #         "temperature": temperature,
    #         "mode": mode,
    #         "user_id": user_id or userId,
    #         "instructions": instructions,
    #         "response_format": response_format or responseFormat,
    #         "include_graph": include_graph if include_graph is not None else includeGraph,
    #         "filters": filters,
    #     }
    #     body["stream"] = True
    #     response = self._client.request_stream("POST", "/memories/query", json=body)
    #     return SSEIterator(response)


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


class AsyncMemories:
    """Asynchronous interface for the Memories API.

    Access via ``mk.memories`` on :class:`AsyncMemoryKit`.
    """

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        content: str,
        *,
        title: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        language: Optional[str] = None,
        format: Optional[str] = None,
    ) -> Memory:
        """Create a new memory. See :meth:`Memories.create` for details."""
        body: Dict[str, Any] = {
            "content": content,
            "title": title,
            "type": type,
            "tags": tags,
            "metadata": metadata,
            "user_id": user_id or userId,
            "language": language,
            "format": format,
        }
        data = await self._client.request("POST", "/memories", json=body)
        return Memory(data)

    async def batch_create(
        self,
        items: List[Dict[str, Any]],
        *,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> BatchIngestResponse:
        """Batch ingest memories. See :meth:`Memories.batch_create`."""
        body: Dict[str, Any] = {"items": items}
        if defaults is not None:
            body["defaults"] = defaults
        data = await self._client.request("POST", "/memories/batch", json=body)
        return BatchIngestResponse(data)

    async def upload(
        self,
        file: Any,
        *,
        title: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[str] = None,
        language: Optional[str] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> Memory:
        """Upload a file as a memory. See :meth:`Memories.upload`."""
        if isinstance(file, tuple):
            files = {"file": file}
        else:
            files = {"file": file}

        form_data: Dict[str, Any] = {}
        if title is not None:
            form_data["title"] = title
        if type is not None:
            form_data["type"] = type
        if tags is not None:
            form_data["tags"] = ",".join(tags) if isinstance(tags, list) else tags
        if metadata is not None:
            form_data["metadata"] = metadata
        if language is not None:
            form_data["language"] = language

        uid = user_id or userId
        if uid is not None:
            form_data["userId"] = uid

        data = await self._client.request(
            "POST", "/memories/upload", files=files, data=form_data
        )
        return Memory(data)

    async def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
    ) -> MemoryList:
        """List memories. See :meth:`Memories.list`."""
        params: Dict[str, Any] = {
            "limit": limit,
            "cursor": cursor,
            "status": status,
            "type": type,
            "user_id": user_id or userId,
        }
        data = await self._client.request("GET", "/memories", params=params)
        return MemoryList(data)

    async def get(self, memory_id: str) -> Memory:
        """Get a memory by ID. See :meth:`Memories.get`."""
        data = await self._client.request("GET", f"/memories/{memory_id}")
        return Memory(data)

    async def update(
        self,
        memory_id: str,
        *,
        title: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content: Optional[str] = None,
    ) -> Memory:
        """Update a memory. See :meth:`Memories.update`."""
        body: Dict[str, Any] = {
            "title": title,
            "type": type,
            "tags": tags,
            "metadata": metadata,
            "content": content,
        }
        data = await self._client.request("PUT", f"/memories/{memory_id}", json=body)
        return Memory(data)

    async def reprocess(self, memory_id: str) -> Memory:
        """Reprocess a memory. See :meth:`Memories.reprocess`."""
        data = await self._client.request("POST", f"/memories/{memory_id}/reprocess")
        return Memory(data)

    async def delete(self, memory_id: str) -> None:
        """Soft-delete a memory. See :meth:`Memories.delete`."""
        await self._client.request("DELETE", f"/memories/{memory_id}")

    # V2: query endpoint disabled for initial launch
    # async def query(
    #     self,
    #     query: str,
    #     *,
    #     max_sources: Optional[int] = None,
    #     maxSources: Optional[int] = None,
    #     temperature: Optional[float] = None,
    #     mode: Optional[str] = None,
    #     user_id: Optional[str] = None,
    #     userId: Optional[str] = None,
    #     instructions: Optional[str] = None,
    #     response_format: Optional[str] = None,
    #     responseFormat: Optional[str] = None,
    #     include_graph: Optional[bool] = None,
    #     includeGraph: Optional[bool] = None,
    #     filters: Optional[Dict[str, Any]] = None,
    # ) -> QueryResponse:
    #     body: Dict[str, Any] = {
    #         "query": query,
    #         "max_sources": max_sources or maxSources,
    #         "temperature": temperature,
    #         "mode": mode,
    #         "user_id": user_id or userId,
    #         "instructions": instructions,
    #         "response_format": response_format or responseFormat,
    #         "include_graph": include_graph if include_graph is not None else includeGraph,
    #         "filters": filters,
    #     }
    #     data = await self._client.request("POST", "/memories/query", json=body)
    #     return QueryResponse(data)

    async def search(
        self,
        query: str,
        *,
        precision: Optional[str] = None,
        limit: Optional[int] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        type: Optional[str] = None,
        tags: Optional[Union[List[str], str]] = None,
        created_after: Optional[Union[str, datetime]] = None,
        created_before: Optional[Union[str, datetime]] = None,
        include_graph: Optional[bool] = None,
        includeGraph: Optional[bool] = None,
    ) -> SearchResponse:
        """Hybrid search. See :meth:`Memories.search` for details."""
        if isinstance(tags, list):
            tags = ",".join(tags)
        if isinstance(created_after, datetime):
            created_after = created_after.isoformat()
        if isinstance(created_before, datetime):
            created_before = created_before.isoformat()

        params: Dict[str, Any] = {
            "query": query,
            "precision": precision,
            "limit": limit,
            "user_id": user_id or userId,
            "type": type,
            "tags": tags,
            "created_after": created_after,
            "created_before": created_before,
            "include_graph": include_graph if include_graph is not None else includeGraph,
        }
        data = await self._client.request("GET", "/memories/search", params=params)
        return SearchResponse(data)

    # V2: streaming disabled for initial launch
    # async def stream(
    #     self,
    #     query: str,
    #     *,
    #     max_sources: Optional[int] = None,
    #     maxSources: Optional[int] = None,
    #     temperature: Optional[float] = None,
    #     mode: Optional[str] = None,
    #     user_id: Optional[str] = None,
    #     userId: Optional[str] = None,
    #     instructions: Optional[str] = None,
    #     response_format: Optional[str] = None,
    #     responseFormat: Optional[str] = None,
    #     include_graph: Optional[bool] = None,
    #     includeGraph: Optional[bool] = None,
    #     filters: Optional[Dict[str, Any]] = None,
    # ) -> AsyncSSEIterator:
    #     body: Dict[str, Any] = {
    #         "query": query,
    #         "max_sources": max_sources or maxSources,
    #         "temperature": temperature,
    #         "mode": mode,
    #         "user_id": user_id or userId,
    #         "instructions": instructions,
    #         "response_format": response_format or responseFormat,
    #         "include_graph": include_graph if include_graph is not None else includeGraph,
    #         "filters": filters,
    #     }
    #     body["stream"] = True
    #     response = await self._client.request_stream("POST", "/memories/query", json=body)
    #     return AsyncSSEIterator(response)
