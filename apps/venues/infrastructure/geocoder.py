"""Geocoding utility - uses Google Maps API when key available, no-op otherwise."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from django.conf import settings


def geocode_address(address: str) -> tuple[float, float] | None:
    """Return (lat, lng) for an address using Google Maps Geocoding API.

    Returns None if no API key configured or address not found.

    @param address - the full address string to geocode
    @returns (latitude, longitude) tuple or None
    """
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return None
    try:
        params = urllib.parse.urlencode({"address": address, "key": api_key})
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{params}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        if results:
            loc = results[0]["geometry"]["location"]
            return (loc["lat"], loc["lng"])
    except Exception:
        pass
    return None
