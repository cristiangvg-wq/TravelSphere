from datetime import date
from urllib.parse import quote_plus

CURRENCY_RATES = {"COP": 1, "USD": 1/4000, "EUR": 1/4300}

def money(value: float, currency: str = "COP") -> str:
    converted = value * CURRENCY_RATES.get(currency, 1)
    if currency == "COP":
        return f"${converted:,.0f} COP".replace(",", ".")
    return f"{converted:,.2f} {currency}"

def duration_days(start: date, end: date) -> int:
    return max(0, (end - start).days)

def search_url(provider: str, trip: dict) -> str:
    origin, dest = quote_plus(trip["origin"]), quote_plus(trip["destination"])
    dep, ret = trip["departure"].isoformat(), trip["return_date"].isoformat()
    query = quote_plus(f"{trip['origin']} {trip['destination']} {dep} {ret}")
    urls = {
        "kayak": f"https://www.kayak.com/flights/{origin}-{dest}/{dep}/{ret}",
        "skyscanner": f"https://www.skyscanner.net/transport/flights/{origin}/{dest}/{dep}/{ret}/",
        "google_flights": f"https://www.google.com/travel/flights?q={query}",
        "booking": f"https://www.booking.com/searchresults.html?ss={dest}&checkin={dep}&checkout={ret}",
        "airbnb": f"https://www.airbnb.com/s/{dest}/homes?checkin={dep}&checkout={ret}",
        "maps": f"https://www.google.com/maps/search/?api=1&query={dest}",
    }
    return urls.get(provider, f"https://www.google.com/search?q={query}")
