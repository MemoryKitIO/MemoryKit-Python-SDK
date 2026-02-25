"""Webhooks resource — register, list, test, and manage webhooks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._client import AsyncHTTPClient, SyncHTTPClient
from ._types import Webhook, WebhookList, WebhookTestResponse


class Webhooks:
    """Synchronous interface for the Webhooks API.

    Access via ``mk.webhooks``.
    """

    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client

    def create(
        self,
        *,
        url: str,
        events: List[str],
    ) -> Webhook:
        """Register a new webhook.

        Args:
            url: The webhook endpoint URL (required).
            events: List of event types to subscribe to (required).

        Returns:
            The created :class:`Webhook` object, including the signing ``secret``.
        """
        body: Dict[str, Any] = {
            "url": url,
            "events": events,
        }
        data = self._client.request("POST", "/webhooks", json=body)
        return Webhook(data)

    def list(self) -> WebhookList:
        """List all registered webhooks.

        Returns:
            A :class:`WebhookList` containing all webhooks.
        """
        data = self._client.request("GET", "/webhooks")
        return WebhookList(data)

    def get(self, webhook_id: str) -> Webhook:
        """Get a webhook by ID.

        Args:
            webhook_id: The webhook ID.

        Returns:
            The :class:`Webhook` object.
        """
        data = self._client.request("GET", f"/webhooks/{webhook_id}")
        return Webhook(data)

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook.

        Args:
            webhook_id: The webhook ID.
        """
        self._client.request("DELETE", f"/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> WebhookTestResponse:
        """Send a test event to a webhook.

        Args:
            webhook_id: The webhook ID.

        Returns:
            A :class:`WebhookTestResponse` with ``success`` and ``status_code``.
        """
        data = self._client.request("POST", f"/webhooks/{webhook_id}/test")
        return WebhookTestResponse(data)


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


class AsyncWebhooks:
    """Asynchronous interface for the Webhooks API.

    Access via ``mk.webhooks`` on :class:`AsyncMemoryKit`.
    """

    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        url: str,
        events: List[str],
    ) -> Webhook:
        """Register a webhook. See :meth:`Webhooks.create`."""
        body: Dict[str, Any] = {
            "url": url,
            "events": events,
        }
        data = await self._client.request("POST", "/webhooks", json=body)
        return Webhook(data)

    async def list(self) -> WebhookList:
        """List all webhooks. See :meth:`Webhooks.list`."""
        data = await self._client.request("GET", "/webhooks")
        return WebhookList(data)

    async def get(self, webhook_id: str) -> Webhook:
        """Get a webhook. See :meth:`Webhooks.get`."""
        data = await self._client.request("GET", f"/webhooks/{webhook_id}")
        return Webhook(data)

    async def delete(self, webhook_id: str) -> None:
        """Delete a webhook. See :meth:`Webhooks.delete`."""
        await self._client.request("DELETE", f"/webhooks/{webhook_id}")

    async def test(self, webhook_id: str) -> WebhookTestResponse:
        """Test a webhook. See :meth:`Webhooks.test`."""
        data = await self._client.request("POST", f"/webhooks/{webhook_id}/test")
        return WebhookTestResponse(data)
