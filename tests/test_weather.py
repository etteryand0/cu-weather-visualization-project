import unittest

from cu_weather_app.weather import check_bad_weather


class TestCheckBadWeather(unittest.TestCase):
    def test_good_weather(self):
        self.assertEqual(check_bad_weather(20, 10, 30, 50), "Хорошие погодные условия")

    def test_high_temperature(self):
        self.assertEqual(check_bad_weather(36, 10, 30, 50), "Плохие погодные условия")

    def test_low_temperature(self):
        self.assertEqual(check_bad_weather(-5, 10, 30, 50), "Плохие погодные условия")

    def test_high_wind_speed(self):
        self.assertEqual(check_bad_weather(20, 60, 30, 50), "Плохие погодные условия")

    def test_high_precipitation_probability(self):
        self.assertEqual(check_bad_weather(20, 10, 80, 50), "Плохие погодные условия")

    def test_high_humidity(self):
        self.assertEqual(check_bad_weather(20, 10, 30, 95), "Плохие погодные условия")

    def test_edge_case(self):
        self.assertEqual(check_bad_weather(0, 50, 70, 90), "Плохие погодные условия")
        self.assertEqual(check_bad_weather(35, 50, 70, 90), "Плохие погодные условия")
        self.assertEqual(check_bad_weather(20, 50, 70, 90), "Плохие погодные условия")
        self.assertEqual(check_bad_weather(20, 50, 71, 90), "Плохие погодные условия")


if __name__ == "__main__":
    unittest.main()
