import unittest
from unittest.mock import patch, AsyncMock
import logging

# Импорт функций из модуля с бизнес-логикой (путь заменить на актуальный)
from bot.weather import get_coords, get_weather, get_weather_by_city

class TestWeather(unittest.IsolatedAsyncioTestCase):

    @patch("aiohttp.ClientSession.get")
    async def test_get_coords_success(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": {
                "GeoObjectCollection": {
                    "featureMember": [
                        {
                            "GeoObject": {
                                "Point": {"pos": "37.617635 55.755814"}
                            }
                        }
                    ]
                }
            }
        }
        mock_get.return_value.__aenter__.return_value = mock_response

        coords = await get_coords("Москва")
        self.assertEqual(coords, (55.755814, 37.617635))

    @patch("aiohttp.ClientSession.get")
    async def test_get_coords_error_status(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 500  # Ошибка сервера
        mock_get.return_value.__aenter__.return_value = mock_response

        with self.assertLogs(level="ERROR") as log:
            coords = await get_coords("Неизвестный город")
            self.assertIsNone(coords)
            self.assertTrue(any("Ошибка при геокодинге города" in message for message in log.output))

    @patch("aiohttp.ClientSession.get")
    async def test_get_weather_success(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"fact": {"temp": 20, "condition": "clear"}}
        mock_get.return_value.__aenter__.return_value = mock_response

        weather = await get_weather(55.755814, 37.617635)
        self.assertIn("fact", weather)
        self.assertEqual(weather["fact"]["temp"], 20)

    async def test_get_weather_by_city_success(self):
        coords = (55.755814, 37.617635)
        weather_response = {"fact": {"temp": 20}}

        async def mock_get_coords(city):
            return coords

        async def mock_get_weather(lat, lon):
            self.assertEqual((lat, lon), coords)
            return weather_response

        with patch("bot.weather.get_coords", side_effect=mock_get_coords):
            with patch("bot.weather.get_weather", side_effect=mock_get_weather):
                result = await get_weather_by_city("Москва")
                self.assertEqual(result, weather_response)

if __name__ == "__main__":
    unittest.main()
