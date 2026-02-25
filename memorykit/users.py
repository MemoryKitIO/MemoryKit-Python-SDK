"""Users resource — manage users and user events."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._client import AsyncHTTPClient, SyncHTTPClient
from ._types import Event, EventList, User


class Users:
    """Synchronous interface for the Users API.

    Access via ``mk.users``.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    # -- Users ---------------------------------------------------------------

    def upsert(
        self,
        id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Create or update a user (idempotent).

        Args:
            id: External user ID (required).
            email: User email address.
            name: User display name.
            metadata: Arbitrary metadata dict.

        Returns:
            The :class:`User` object.
        """
        body: Dict[str, Any] = {
            "id": id,
            "email": email,
            "name": name,
            "metadata": metadata,
        }
        data = self._client.request("POST", "/users", json=body)
        return User(data)

    def get(self, user_id: str) -> User:
        """Get a user by their external ID.

        Args:
            user_id: The external user ID.

        Returns:
            The :class:`User` object.
        """
        data = self._client.request("GET", f"/users/{user_id}")
        return User(data)

    def update(
        self,
        user_id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Update an existing user.

        Args:
            user_id: The external user ID.
            email: New email address.
            name: New display name.
            metadata: New metadata.

        Returns:
            The updated :class:`User` object.
        """
        body: Dict[str, Any] = {
            "email": email,
            "name": name,
            "metadata": metadata,
        }
        data = self._client.request("PUT", f"/users/{user_id}", json=body)
        return User(data)

    def delete(
        self,
        user_id: str,
        *,
        cascade: Optional[bool] = None,
    ) -> None:
        """Soft-delete a user.

        Args:
            user_id: The external user ID.
            cascade: If ``True``, also delete the user's memories and chats.
        """
        params: Dict[str, Any] = {}
        if cascade is not None:
            params["cascade"] = str(cascade).lower()
        self._client.request("DELETE", f"/users/{user_id}", params=params if params else None)

    # -- Events --------------------------------------------------------------

    def create_event(
        self,
        user_id: str,
        *,
        type: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """Create a user event.

        Args:
            user_id: The external user ID.
            type: Event type (required), e.g. ``"page_view"``.
            data: Event payload.

        Returns:
            The created :class:`Event` object.
        """
        body: Dict[str, Any] = {
            "type": type,
            "data": data,
        }
        resp = self._client.request("POST", f"/users/{user_id}/events", json=body)
        return Event(resp)

    def list_events(
        self,
        user_id: str,
        *,
        limit: Optional[int] = None,
        type: Optional[str] = None,
    ) -> EventList:
        """List events for a user.

        Args:
            user_id: The external user ID.
            limit: Maximum results (default 20).
            type: Filter by event type.

        Returns:
            An :class:`EventList` with ``data``.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "type": type,
        }
        resp = self._client.request("GET", f"/users/{user_id}/events", params=params)
        return EventList(resp)

    def delete_event(self, user_id: str, event_id: str) -> None:
        """Delete a user event.

        Args:
            user_id: The external user ID.
            event_id: The event ID.
        """
        self._client.request("DELETE", f"/users/{user_id}/events/{event_id}")


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


class AsyncUsers:
    """Asynchronous interface for the Users API.

    Access via ``mk.users`` on :class:`AsyncMemoryKit`.
    """

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def upsert(
        self,
        id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Create or update a user. See :meth:`Users.upsert`."""
        body: Dict[str, Any] = {
            "id": id,
            "email": email,
            "name": name,
            "metadata": metadata,
        }
        data = await self._client.request("POST", "/users", json=body)
        return User(data)

    async def get(self, user_id: str) -> User:
        """Get a user. See :meth:`Users.get`."""
        data = await self._client.request("GET", f"/users/{user_id}")
        return User(data)

    async def update(
        self,
        user_id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> User:
        """Update a user. See :meth:`Users.update`."""
        body: Dict[str, Any] = {
            "email": email,
            "name": name,
            "metadata": metadata,
        }
        data = await self._client.request("PUT", f"/users/{user_id}", json=body)
        return User(data)

    async def delete(
        self,
        user_id: str,
        *,
        cascade: Optional[bool] = None,
    ) -> None:
        """Soft-delete a user. See :meth:`Users.delete`."""
        params: Dict[str, Any] = {}
        if cascade is not None:
            params["cascade"] = str(cascade).lower()
        await self._client.request(
            "DELETE", f"/users/{user_id}", params=params if params else None
        )

    async def create_event(
        self,
        user_id: str,
        *,
        type: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """Create a user event. See :meth:`Users.create_event`."""
        body: Dict[str, Any] = {
            "type": type,
            "data": data,
        }
        resp = await self._client.request("POST", f"/users/{user_id}/events", json=body)
        return Event(resp)

    async def list_events(
        self,
        user_id: str,
        *,
        limit: Optional[int] = None,
        type: Optional[str] = None,
    ) -> EventList:
        """List events for a user. See :meth:`Users.list_events`."""
        params: Dict[str, Any] = {
            "limit": limit,
            "type": type,
        }
        resp = await self._client.request("GET", f"/users/{user_id}/events", params=params)
        return EventList(resp)

    async def delete_event(self, user_id: str, event_id: str) -> None:
        """Delete a user event. See :meth:`Users.delete_event`."""
        await self._client.request("DELETE", f"/users/{user_id}/events/{event_id}")
