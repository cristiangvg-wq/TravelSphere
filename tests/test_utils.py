from datetime import date

from travelsphere.utils import duration_days, money, search_url


def test_duration_days():
    assert duration_days(date(2026, 10, 1), date(2026, 10, 8)) == 7
    assert duration_days(date(2026, 10, 8), date(2026, 10, 1)) == 0


def test_money_formats_supported_currencies():
    assert money(1200, "COP") == "$1.200 COP"
    assert money(4000, "USD") == "1.00 USD"


def test_flight_search_url_includes_trip_dates():
    trip = {
        "origin": "Bogotá",
        "destination": "Ciudad de México",
        "departure": date(2026, 11, 1),
        "return_date": date(2026, 11, 8),
    }
    url = search_url("google_flights", trip)
    assert "2026-11-01" in url
    assert "2026-11-08" in url
