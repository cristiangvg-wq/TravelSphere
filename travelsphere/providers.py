"""Optional, production-oriented adapters for authorized travel APIs.

No provider is called unless its credentials are configured. All requests use timeouts,
bounded result counts, and explicit errors so the UI can fall back to labelled demo data.
"""
from __future__ import annotations

import os
from typing import Any

import requests

AMAD_BASE = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com").rstrip("/")
GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
TIMEOUT = (4, 18)

# Friendly fallbacks in case the provider omits its carrier dictionary.
AIRLINE_NAMES = {
    "AV": "Avianca",
    "LA": "LATAM Airlines",
    "4C": "LATAM Airlines Colombia",
    "CM": "Copa Airlines",
    "AM": "Aeroméxico",
    "AR": "Aerolíneas Argentinas",
    "UA": "United Airlines",
    "AA": "American Airlines",
    "DL": "Delta Air Lines",
    "IB": "Iberia",
    "AF": "Air France",
    "KL": "KLM",
    "AC": "Air Canada",
    "BA": "British Airways",
    "LH": "Lufthansa",
    "UX": "Air Europa",
    "NK": "Spirit Airlines",
    "B6": "JetBlue",
    "WN": "Southwest Airlines",
}


def airline_display_name(carrier_code: str, carriers: dict[str, str] | None = None) -> str:
    """Return a readable carrier name even when Amadeus omits its dictionary."""
    code = str(carrier_code or "").strip().upper()
    if carriers and carriers.get(code):
        return str(carriers[code])
    if code in AIRLINE_NAMES:
        return AIRLINE_NAMES[code]
    return f"Aerolínea ({code})" if code else "Aerolínea no identificada"


class ProviderError(RuntimeError):
    """A provider request failed or returned an unexpected response."""


def _setting(name: str) -> str:
    """Read a setting from environment first, then Streamlit secrets if available."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st
        value = str(st.secrets.get(name, "")).strip()
    except Exception:
        value = ""
    return value


def amadeus_configured() -> bool:
    return bool(_setting("AMADEUS_CLIENT_ID") and _setting("AMADEUS_CLIENT_SECRET"))


def google_places_configured() -> bool:
    return bool(_setting("GOOGLE_PLACES_API_KEY"))


def _amadeus_token() -> str:
    client_id = _setting("AMADEUS_CLIENT_ID")
    client_secret = _setting("AMADEUS_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ProviderError("Amadeus no está configurado.")
    try:
        response = requests.post(
            f"{AMAD_BASE}/v1/security/oauth2/token",
            data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ProviderError("Amadeus no devolvió un token de acceso.")
        return token
    except requests.RequestException as exc:
        raise ProviderError(f"No fue posible autenticar con Amadeus: {exc}") from exc


def _amadeus_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    token = _amadeus_token()
    try:
        response = requests.get(
            f"{AMAD_BASE}{path}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ProviderError("Respuesta inesperada de Amadeus.")
        return payload
    except requests.RequestException as exc:
        detail = ""
        if getattr(exc, "response", None) is not None:
            detail = f" (HTTP {exc.response.status_code})"
        raise ProviderError(f"Consulta Amadeus fallida{detail}.") from exc


def resolve_city_code(keyword: str) -> str | None:
    """Resolve a city name to an Amadeus IATA city code; never guess a code."""
    if not keyword.strip():
        return None
    payload = _amadeus_get(
        "/v1/reference-data/locations",
        {"keyword": keyword.split(",")[0].strip(), "subType": "CITY", "page[limit]": 5},
    )
    for item in payload.get("data", []):
        code = item.get("iataCode")
        if code and len(code) == 3:
            return code.upper()
    return None


def search_flights(trip: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    """Return normalized flight offers, or raise ProviderError; prices are provider quotes."""
    origin = resolve_city_code(str(trip.get("origin", "")))
    destination = resolve_city_code(str(trip.get("destination", "")))
    if not origin or not destination:
        raise ProviderError("No se pudo resolver origen/destino a códigos IATA de ciudad.")
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": trip["departure"].isoformat(),
        "returnDate": trip["return_date"].isoformat(),
        "adults": max(1, int(trip.get("adults", 1))),
        "currencyCode": "COP",
        "max": max(1, min(int(limit), 10)),
    }
    children = int(trip.get("children", 0))
    if children > 0:
        params["children"] = children
    payload = _amadeus_get("/v2/shopping/flight-offers", params)
    results = []
    dictionaries = payload.get("dictionaries", {})
    carriers = dictionaries.get("carriers", {})
    for offer in payload.get("data", []):
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            continue
        first_segments = itineraries[0].get("segments", [])
        last_segments = itineraries[-1].get("segments", []) if len(itineraries) > 1 else []
        if not first_segments:
            continue
        price = offer.get("price", {})
        try:
            total = float(price.get("grandTotal", price.get("total")))
        except (TypeError, ValueError):
            continue
        carrier = first_segments[0].get("carrierCode", "N/D")
        results.append({
            "airline": airline_display_name(carrier, carriers),
            "stops": "Directo" if len(first_segments) == 1 else ("1 escala" if len(first_segments) == 2 else "2+ escalas"),
            "depart": first_segments[0].get("departure", {}).get("at", "")[11:16] or "N/D",
            "arrive": first_segments[-1].get("arrival", {}).get("at", "")[11:16] or "N/D",
            "duration": itineraries[0].get("duration", "N/D").replace("PT", "").lower(),
            "baggage": "Equipaje según tarifa seleccionada",
            "price": total / max(1, int(trip.get("adults", 1)) + int(trip.get("children", 0))),
            "currency": price.get("currency", "COP"),
            "source": "Amadeus",
            "offer_id": offer.get("id", ""),
        })
    return results


def search_hotels(trip: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    """Fetch hotel offers for the resolved destination city; availability is provider-dependent."""
    city_code = resolve_city_code(str(trip.get("destination", "")))
    if not city_code:
        raise ProviderError("No se pudo resolver el destino a un código IATA de ciudad.")
    hotel_payload = _amadeus_get(
        "/v1/reference-data/locations/hotels/by-city",
        {"cityCode": city_code, "radius": 10, "radiusUnit": "KM", "hotelSource": "ALL"},
    )
    hotels = hotel_payload.get("data", [])[:max(1, min(int(limit), 5))]
    results = []
    for hotel in hotels:
        hotel_id = hotel.get("hotelId")
        if not hotel_id:
            continue
        offers = _amadeus_get(
            "/v3/shopping/hotel-offers",
            {
                "hotelIds": hotel_id,
                "adults": max(1, int(trip.get("adults", 1))),
                "checkInDate": trip["departure"].isoformat(),
                "checkOutDate": trip["return_date"].isoformat(),
                "roomQuantity": 1,
                "currency": "COP",
            },
        ).get("data", [])
        for item in offers[:1]:
            offer_list = item.get("offers", [])
            if not offer_list:
                continue
            price = offer_list[0].get("price", {})
            try:
                total = float(price.get("total", 0))
            except (TypeError, ValueError):
                continue
            results.append({
                "name": item.get("hotel", {}).get("name", "Hotel"),
                "kind": "Oferta hotelera",
                "rating": item.get("hotel", {}).get("rating", "N/D"),
                "area": item.get("hotel", {}).get("cityCode", city_code),
                "amenities": ["Oferta consultada en Amadeus"],
                "nightly": total / max(1, (trip["return_date"] - trip["departure"]).days),
                "total": total,
                "currency": price.get("currency", "COP"),
                "source": "Amadeus",
            })
    return results


def search_restaurants(destination: str, limit: int = 8) -> list[dict[str, Any]]:
    """Search Google Places text search and normalize fields used by the UI."""
    api_key = _setting("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise ProviderError("Google Places no está configurado.")
    try:
        response = requests.post(
            GOOGLE_PLACES_URL,
            json={"textQuery": f"restaurants in {destination}", "pageSize": max(1, min(int(limit), 20))},
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.rating,places.formattedAddress,places.googleMapsUri,places.priceLevel,places.primaryTypeDisplayName",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise ProviderError("Consulta Google Places fallida.") from exc
    levels = {"PRICE_LEVEL_INEXPENSIVE": "Económico", "PRICE_LEVEL_MODERATE": "Moderado", "PRICE_LEVEL_EXPENSIVE": "Premium", "PRICE_LEVEL_VERY_EXPENSIVE": "Premium"}
    results = []
    for place in payload.get("places", []):
        name = place.get("displayName", {}).get("text", "Restaurante")
        results.append({
            "name": name,
            "cuisine": place.get("primaryTypeDisplayName", {}).get("text", "Local"),
            "price_level": levels.get(place.get("priceLevel"), "Todos"),
            "rating": place.get("rating", "N/D"),
            "description": place.get("formattedAddress", "Dirección no disponible"),
            "avg_cost": 0,
            "maps_url": place.get("googleMapsUri", ""),
            "source": "Google Places",
        })
    return results
