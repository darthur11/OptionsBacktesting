import datetime
import unittest
import ujson

from source.utils import *
class MyTestCase(unittest.TestCase):
    def test_enum(self):
        print(dateFormats.ddmmyyyy_point.value)
        print(type(dateFormats.yyyymmdd_dash))
    def test_convert_string_to_date(self):
        test_value = convert_string_to_datetime('2022-01-01', dateFormats.yyyymmdd_dash)
        expected_value = datetime.datetime(2022,1,1, tzinfo=datetime.timezone.utc)
        self.assertEqual(expected_value, test_value)  # add assertion here

    def test_convert_timestamp_to_date(self):
        test_value = convert_timestamp_to_datetime(1672808545)
        expected_value = datetime.datetime(2023,1,4,5,2,25, tzinfo=datetime.timezone.utc)
        self.assertEqual(expected_value, test_value)

    def test_min_hour(self):
        with open("/Users/dossatayev/PycharmProjects/OptionsDataGrabber/input_data.json", 'r') as f:
            output = ujson.load(f)
        dates_fin = list(output.keys())

        #print(tuple(set(([convert_timestamp_to_datetime(int(val)).hour for val in dates_fin])))[1:-1])
        self.assertEqual(1,1)


if __name__ == '__main__':
    unittest.main()
