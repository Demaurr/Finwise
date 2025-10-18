import requests

def get_country_code(country_name):
    """Return ISO3 code using REST Countries API."""
    try:
        res = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        if res.status_code == 200:
            data = res.json()
            return data[0]["cca3"]
    except Exception:
        pass
    return None


def get_country_indicator(country_code, indicator="NY.GNS.ICTR.ZS"):
    """Fetch latest World Bank indicator value for a country."""
    try:
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 1 and isinstance(data[1], list):
                for record in data[1]:
                    if record.get("value") is not None:
                        return {
                            "year": record["date"],
                            "value": round(record["value"], 2),
                            "indicator": record["indicator"]["value"]
                        }
    except Exception:
        pass
    return {"year": None, "value": None, "indicator": 'Gross savings (% of GDP)'}

if __name__ == "__main__":
    print(get_country_indicator("PK"))