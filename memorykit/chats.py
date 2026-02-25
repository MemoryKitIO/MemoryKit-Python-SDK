"""Chats resource — create chat sessions, send messages, and stream responses."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._client import AsyncHTTPClient, SyncHTTPClient
from ._sse import AsyncSSEIterator, SSEIterator
from ._types import Chat, ChatHistory, ChatList, ChatMessage, ChatMessageResponse


class Chats:
    """Synchronous interface for the Chats API.

    Access via ``mk.chats``.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Chat:
        """Create a new chat session.

        Args:
            user_id: User ID to associate (snake_case).
            userId: User ID to associate (camelCase).
            title: Chat title.
            metadata: Arbitrary metadata.

        Returns:
            The created :class:`Chat` object.
        """
        body: Dict[str, Any] = {
            "user_id": user_id or userId,
            "title": title,
            "metadata": metadata,
        }
        data = self._client.request("POST", "/chats", json=body)
        return Chat(data)

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ChatList:
        """List chats with cursor-based pagination.

        Args:
            user_id: Filter by user ID (snake_case).
            userId: Filter by user ID (camelCase).
            limit: Maximum results (default 20).
            cursor: Pagination cursor.

        Returns:
            A :class:`ChatList` with ``data`` and ``has_more``.
        """
        params: Dict[str, Any] = {
            "user_id": user_id or userId,
            "limit": limit,
            "cursor": cursor,
        }
        data = self._client.request("GET", "/chats", params=params)
        return ChatList(data)

    def get_history(self, chat_id: str) -> ChatHistory:
        """Get a chat with its full message history.

        Args:
            chat_id: The chat ID.

        Returns:
            A :class:`ChatHistory` with ``id``, ``title``, and ``messages``.
        """
        data = self._client.request("GET", f"/chats/{chat_id}")
        return ChatHistory(data)

    def send_message(
        self,
        chat_id: str,
        *,
        message: str,
        mode: Optional[str] = None,
        max_sources: Optional[int] = None,
        maxSources: Optional[int] = None,
        temperature: Optional[float] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        instructions: Optional[str] = None,
        response_format: Optional[str] = None,
        responseFormat: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ChatMessageResponse:
        """Send a message in a chat and receive a response.

        Args:
            chat_id: The chat ID.
            message: The user message content (required).
            mode: Query mode.
            max_sources: Maximum source documents.
            temperature: LLM temperature.
            user_id: User ID.
            instructions: Additional LLM instructions.
            response_format: Desired response format.
            filters: Filter object.

        Returns:
            A :class:`ChatMessageResponse` containing the assistant's
            :class:`ChatMessage`.
        """
        body: Dict[str, Any] = {
            "message": message,
            "mode": mode,
            "max_sources": max_sources or maxSources,
            "temperature": temperature,
            "user_id": user_id or userId,
            "instructions": instructions,
            "response_format": response_format or responseFormat,
            "filters": filters,
        }
        data = self._client.request("POST", f"/chats/{chat_id}/messages", json=body)
        return ChatMessageResponse(data)

    def stream_message(
        self,
        chat_id: str,
        *,
        message: str,
        mode: Optional[str] = None,
        max_sources: Optional[int] = None,
        maxSources: Optional[int] = None,
        temperature: Optional[float] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        instructions: Optional[str] = None,
        response_format: Optional[str] = None,
        responseFormat: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SSEIterator:
        """Stream a message response using Server-Sent Events.

        Yields dicts with ``event`` and ``data`` keys.

        Args:
            chat_id: The chat ID.
            message: The user message content (required).
            mode: Query mode.
            max_sources: Maximum source documents.
            temperature: LLM temperature.
            user_id: User ID.
            instructions: Additional LLM instructions.
            response_format: Desired response format.
            filters: Filter object.

        Returns:
            An :class:`SSEIterator` that yields event dicts.

        Example::

            for event in mk.chats.stream_message("chat_abc", message="Hello"):
                if event["event"] == "text":
                    print(event["data"]["content"], end="")
        """
        body: Dict[str, Any] = {
            "message": message,
            "mode": mode,
            "max_sources": max_sources or maxSources,
            "temperature": temperature,
            "user_id": user_id or userId,
            "instructions": instructions,
            "response_format": response_format or responseFormat,
            "filters": filters,
        }
        response = self._client.request_stream(
            "POST", f"/chats/{chat_id}/messages/stream", json=body
        )
        return SSEIterator(response)

    def delete(self, chat_id: str) -> None:
        """Soft-delete a chat.

        Args:
            chat_id: The chat ID.
        """
        self._client.request("DELETE", f"/chats/{chat_id}")


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


class AsyncChats:
    """Asynchronous interface for the Chats API.

    Access via ``mk.chats`` on :class:`AsyncMemoryKit`.
    """

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Chat:
        """Create a chat. See :meth:`Chats.create`."""
        body: Dict[str, Any] = {
            "user_id": user_id or userId,
            "title": title,
            "metadata": metadata,
        }
        data = await self._client.request("POST", "/chats", json=body)
        return Chat(data)

    async def list(
        self,
        *,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ChatList:
        """List chats. See :meth:`Chats.list`."""
        params: Dict[str, Any] = {
            "user_id": user_id or userId,
            "limit": limit,
            "cursor": cursor,
        }
        data = await self._client.request("GET", "/chats", params=params)
        return ChatList(data)

    async def get_history(self, chat_id: str) -> ChatHistory:
        """Get chat history. See :meth:`Chats.get_history`."""
        data = await self._client.request("GET", f"/chats/{chat_id}")
        return ChatHistory(data)

    async def send_message(
        self,
        chat_id: str,
        *,
        message: str,
        mode: Optional[str] = None,
        max_sources: Optional[int] = None,
        maxSources: Optional[int] = None,
        temperature: Optional[float] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        instructions: Optional[str] = None,
        response_format: Optional[str] = None,
        responseFormat: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ChatMessageResponse:
        """Send a message. See :meth:`Chats.send_message`."""
        body: Dict[str, Any] = {
            "message": message,
            "mode": mode,
            "max_sources": max_sources or maxSources,
            "temperature": temperature,
            "user_id": user_id or userId,
            "instructions": instructions,
            "response_format": response_format or responseFormat,
            "filters": filters,
        }
        data = await self._client.request("POST", f"/chats/{chat_id}/messages", json=body)
        return ChatMessageResponse(data)

    async def stream_message(
        self,
        chat_id: str,
        *,
        message: str,
        mode: Optional[str] = None,
        max_sources: Optional[int] = None,
        maxSources: Optional[int] = None,
        temperature: Optional[float] = None,
        user_id: Optional[str] = None,
        userId: Optional[str] = None,
        instructions: Optional[str] = None,
        response_format: Optional[str] = None,
        responseFormat: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> AsyncSSEIterator:
        """Stream a message. See :meth:`Chats.stream_message`."""
        body: Dict[str, Any] = {
            "message": message,
            "mode": mode,
            "max_sources": max_sources or maxSources,
            "temperature": temperature,
            "user_id": user_id or userId,
            "instructions": instructions,
            "response_format": response_format or responseFormat,
            "filters": filters,
        }
        response = await self._client.request_stream(
            "POST", f"/chats/{chat_id}/messages/stream", json=body
        )
        return AsyncSSEIterator(response)

    async def delete(self, chat_id: str) -> None:
        """Soft-delete a chat. See :meth:`Chats.delete`."""
        await self._client.request("DELETE", f"/chats/{chat_id}")
