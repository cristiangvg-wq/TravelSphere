from travelsphere import providers
from travelsphere.data import build_demo_results


def test_demo_flights_have_visible_example_airline_names():
    trip = {
        "destination": "Ciudad de México, México",
        "adults": 1,
        "children": 0,
    }
    flights = build_demo_results(trip, 2)["flights"]
    assert [flight["airline"] for flight in flights] == [
        "Avianca (ejemplo)",
        "Aeroméxico (ejemplo)",
        "Copa Airlines (ejemplo)",
    ]


def test_resolve_city_code_uses_city_part_and_returns_iata(monkeypatch):
    captured = {}

    def fake_get(path, params):
        captured["path"] = path
        captured["params"] = params
        return {"data": [{"name": "Bogota", "iataCode": "BOG"}]}

    monkeypatch.setattr(providers, "_amadeus_get", fake_get)
    assert providers.resolve_city_code("Bogotá, Colombia") == "BOG"
    assert captured["path"] == "/v1/reference-data/locations"
    assert captured["params"]["keyword"] == "Bogotá"


def test_resolve_city_code_returns_none_when_no_match(monkeypatch):
    monkeypatch.setattr(providers, "_amadeus_get", lambda path, params: {"data": []})
    assert providers.resolve_city_code("Atlantis") is None


def test_empty_city_does_not_call_provider(monkeypatch):
    def unexpected_call(*args, **kwargs):
        raise AssertionError("Provider must not be called for an empty city")

    monkeypatch.setattr(providers, "_amadeus_get", unexpected_call)
    assert providers.resolve_city_code("  ") is None


def test_airline_display_name_uses_provider_dictionary():
    assert providers.airline_display_name("AV", {"AV": "Avianca S.A."}) == "Avianca S.A."


def test_airline_display_name_has_friendly_fallbacks():
    assert providers.airline_display_name("AV") == "Avianca"
    assert providers.airline_display_name("ZZ") == "Aerolínea (ZZ)"
    assert providers.airline_display_name("") == "Aerolínea no identificada"
