"""Unit tests for HttpParticipationContextClient."""

from __future__ import annotations

import json
import urllib.error
import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from apps.volunteers.infrastructure.participation_client import HttpParticipationContextClient


def _make_response(body: dict, status: int = 200) -> MagicMock:
    """Build a fake urllib response context manager."""
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.read.return_value = json.dumps(body).encode()
    mock.status = status
    return mock


def test_is_attendee_returns_true_when_type_is_attendee():
    """Returns True when participation service says participation_type=attendee."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    resp = _make_response({"participation_type": "attendee"})
    with patch("urllib.request.urlopen", return_value=resp):
        assert client.is_attendee(event_id, user_id) is True


def test_is_attendee_returns_false_when_type_is_volunteer():
    """Returns False when participation type is not attendee."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    resp = _make_response({"participation_type": "volunteer"})
    with patch("urllib.request.urlopen", return_value=resp):
        assert client.is_attendee(event_id, user_id) is False


def test_is_attendee_returns_false_on_404():
    """Returns False when the context row does not exist (404)."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    exc = urllib.error.HTTPError(url="", code=404, msg="Not Found", hdrs=None, fp=BytesIO())  # type: ignore[arg-type]
    with patch("urllib.request.urlopen", side_effect=exc):
        assert client.is_attendee(event_id, user_id) is False


def test_is_attendee_raises_on_non_404_http_error():
    """Raises RuntimeError when participation service returns a non-404 error."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    exc = urllib.error.HTTPError(url="", code=500, msg="Server Error", hdrs=None, fp=BytesIO())  # type: ignore[arg-type]
    with patch("urllib.request.urlopen", side_effect=exc):
        with pytest.raises(RuntimeError, match="500"):
            client.is_attendee(event_id, user_id)


def test_is_attendee_raises_on_url_error():
    """Raises RuntimeError when participation service is unreachable."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    exc = urllib.error.URLError("Connection refused")
    with patch("urllib.request.urlopen", side_effect=exc):
        with pytest.raises(RuntimeError, match="Could not reach"):
            client.is_attendee(event_id, user_id)


def test_set_volunteer_posts_correct_payload():
    """set_volunteer sends POST with participation_type=volunteer in the body."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    resp = _make_response({})
    calls: list = []

    def fake_urlopen(req, timeout=None):
        calls.append(req)
        return resp

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        client.set_volunteer(event_id, user_id)

    assert len(calls) == 1
    req = calls[0]
    assert req.method == "POST"
    assert str(event_id) in req.full_url
    assert str(user_id) in req.full_url
    body = json.loads(req.data)
    assert body["participation_type"] == "volunteer"


def test_set_volunteer_raises_on_http_error():
    """Raises RuntimeError when participation service returns an error on POST."""
    client = HttpParticipationContextClient("http://participation:8005")
    event_id = uuid.uuid4()
    user_id = uuid.uuid4()
    exc = urllib.error.HTTPError(url="", code=503, msg="Service Unavailable", hdrs=None, fp=BytesIO())  # type: ignore[arg-type]
    with patch("urllib.request.urlopen", side_effect=exc):
        with pytest.raises(RuntimeError, match="503"):
            client.set_volunteer(event_id, user_id)
