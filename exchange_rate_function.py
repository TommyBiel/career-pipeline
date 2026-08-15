import os
import requests
from dotenv import load_dotenv

load_dotenv('../keys.env')


def exchange_rate_function(currency):

    exchange_rate_key = os.getenv("exchange_key")

    try:
        url=f"https://v6.exchangerate-api.com/v6/{exchange_rate_key}/latest/{currency}"

        exchange_rate_response = requests.get(url, timeout=5)
        exchange_rate_response.raise_for_status()
        exchange_rate_response_json = exchange_rate_response.json()

        return exchange_rate_response_json

    except Exception as e:
        print(e)

# # Two function calls mean that the API uses requests twice!
# exchange_rate_gbp_php = exchange_rate_function("GBP").get("conversion_rates", {}).get("PHP", 0)
# exchange_rate_usd_php = exchange_rate_function("USD").get("conversion_rates", {}).get("PHP", 0)