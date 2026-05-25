"""HTTP adapter for checking and recording participation context in participation-service."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import uuid

from apps.volunteers.domain.repositories import IParticipationContextClient


class HttpParticipationContextClient(IParticipationContextClient):
    """Calls participation-service internal API to query and record participation context."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def is_attendee(self, event_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Return True if user is already registered as an attendee for this event.

        @param event_id - the event to check
        @param user_id - the user to check
        @returns True if an attendee context row exists, False otherwise
        @raises RuntimeError if the participation service is unreachable
        """
        url = f"{self._base_url}/internal/participation-context/{event_id}/{user_id}/"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("participation_type") == "attendee"
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return False
            raise RuntimeError(f"Participation service returned error {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach participation service: {exc}") from exc

    def set_volunteer(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Record the user as a volunteer for this event in participation-service.

        @param event_id - the event
        @param user_id - the approved volunteer
        @raises RuntimeError if the participation service is unreachable
        """
        url = f"{self._base_url}/internal/participation-context/{event_id}/{user_id}/"
        payload = json.dumps({"participation_type": "volunteer"}).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=5):
                pass
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Participation service returned error {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach participation service: {exc}") from exc
