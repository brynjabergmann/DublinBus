import unittest
import requests
import json

class server_test(unittest.TestCase):

    def test_connection_weather_api(self):
        # checks if the weather API connection works"
        url = "https://api.darksky.net/forecast/9a91b8d12a4a4a97d2c0bba6c5d18870/53.3498,-6.2603"
        rawData = requests.get(url)
        self.assertTrue(rawData.status_code == 200)

    def test_city(self):
        # checks for city name of weather API data
        url = "https://api.darksky.net/forecast/9a91b8d12a4a4a97d2c0bba6c5d18870/53.3498,-6.2603"
        rawData = requests.get(url)
        data = json.loads(rawData.text)
        city = data["timezone"]
        self.assertTrue(city == "Europe/Dublin")


if __name__ == "__main__":
    unittest.main()
