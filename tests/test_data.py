"""Small synthetic examples test parsing rules, not hurricane predictions."""
import unittest
from src.stormsight.data import coordinate, parse_hurdat

ROW = '20240926, 1800, L, HU, 25.0N, 85.0W, 100, -999,'

class TrackReaderTests(unittest.TestCase):
    def test_coordinates_and_missing_pressure(self):
        row = parse_hurdat('AL012024, TEST, 1,\n' + ROW).iloc[0]
        self.assertEqual(row.longitude, -85)
        self.assertEqual(row.latitude, 25)
        self.assertIsNone(row.pressure_mb)
        self.assertEqual(row.record_identifier, 'L')
        self.assertEqual(str(row.time_utc), '2024-09-26 18:00:00+00:00')

    def test_truncated_storm_rejected(self):
        with self.assertRaises(ValueError):
            parse_hurdat('AL012024, TEST, 2,\n' + ROW)

    def test_extra_observation_rejected(self):
        with self.assertRaises(ValueError):
            parse_hurdat('AL012024, TEST, 1,\n' + ROW + '\n' + ROW)

    def test_invalid_coordinate_rejected(self):
        with self.assertRaises(ValueError):
            coordinate('91N', True)
        self.assertEqual(coordinate('12.5S', True), -12.5)
        self.assertEqual(coordinate('12.5E', False), 12.5)

    def test_duplicate_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            parse_hurdat('AL012024, TEST, 2,\n' + ROW + '\n' + ROW)

    def test_empty_data_rejected(self):
        with self.assertRaises(ValueError):
            parse_hurdat('')

if __name__ == '__main__':
    unittest.main()
