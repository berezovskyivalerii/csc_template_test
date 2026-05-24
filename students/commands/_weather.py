import requests

from config import get_token


def get_weather(city: str) -> str:
    api_key = get_token("WEATHER_API_KEY")
    if not api_key:
        return "Додайте WEATHER_API_KEY у students/.env"

    city = city.strip()
    if not city:
        return "Вкажіть місто: weather London"

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": api_key, "units": "metric", "lang": "uk"},
        timeout=15,
    )
    if response.status_code != 200:
        return f"Не знайшов погоду для «{city}»"

    data = response.json()
    name = data["name"]
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    return f"{name}: {temp:.1f}°C, {desc}"
