"""Tests for SSE (Server-Sent Events) parser."""


from memorykit._sse import _parse_event_block


class TestParseEventBlock:
    def test_simple_text_event(self):
        block = 'event: text\ndata: {"content": "Hello"}'
        result = _parse_event_block(block)
        assert result is not None
        assert result["event"] == "text"
        assert result["data"] == {"content": "Hello"}

    def test_default_event_type(self):
        block = 'data: {"content": "Hello"}'
        result = _parse_event_block(block)
        assert result is not None
        # No SSE event: header and no "type" key in JSON → fallback "message"
        assert result["event"] == "message"

    def test_done_event(self):
        block = 'event: done\ndata: {"request_id": "req_123"}'
        result = _parse_event_block(block)
        assert result is not None
        assert result["event"] == "done"
        assert result["data"]["request_id"] == "req_123"

    def test_plain_string_data(self):
        block = "data: plain text here"
        result = _parse_event_block(block)
        assert result is not None
        # Non-JSON data is wrapped as a text event matching backend format
        assert result["data"] == {"type": "text", "content": "plain text here"}
        assert result["event"] == "text"

    def test_json_type_field_overrides_sse_event(self):
        """When JSON payload contains a 'type' field, it should be used as event type."""
        block = 'event: text\ndata: {"type": "done", "request_id": "req_456"}'
        result = _parse_event_block(block)
        assert result is not None
        # JSON type "done" overrides SSE event: "text"
        assert result["event"] == "done"
        assert result["data"]["request_id"] == "req_456"

    def test_json_type_field_without_sse_event_header(self):
        """JSON type field should be extracted even without SSE event: header."""
        block = 'data: {"type": "error", "message": "Rate limited"}'
        result = _parse_event_block(block)
        assert result is not None
        assert result["event"] == "error"
        assert result["data"]["message"] == "Rate limited"

    def test_empty_block(self):
        result = _parse_event_block("")
        assert result is None

    def test_comment_only_block(self):
        result = _parse_event_block(": keep-alive")
        assert result is None

    def test_multiline_data(self):
        block = "event: text\ndata: line1\ndata: line2"
        result = _parse_event_block(block)
        assert result is not None
        # Non-JSON multiline data is wrapped as a text event matching backend format
        assert result["data"] == {"type": "text", "content": "line1\nline2"}
        assert result["event"] == "text"

    def test_error_event(self):
        block = 'event: error\ndata: {"message": "Something failed"}'
        result = _parse_event_block(block)
        assert result is not None
        assert result["event"] == "error"
        assert result["data"]["message"] == "Something failed"

    def test_sources_event(self):
        block = 'event: sources\ndata: [{"content": "src1", "score": 0.9}]'
        result = _parse_event_block(block)
        assert result is not None
        assert result["event"] == "sources"
        assert isinstance(result["data"], list)

    def test_usage_event(self):
        block = 'event: usage\ndata: {"total_time_ms": 500, "tokens_used": 200}'
        result = _parse_event_block(block)
        assert result is not None
        assert result["event"] == "usage"
        assert result["data"]["total_time_ms"] == 500


