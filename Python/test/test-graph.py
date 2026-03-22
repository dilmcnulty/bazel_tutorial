import unittest
from graph import clean_splits

class TestSplits(unittest.TestCase):

    def setUp(self):
        """Set up standard test data used across multiple tests."""
        self.splits = {'TSLA': ('2022-08-25', 3.0)}
        self.raw_data = {
            'TSLA': [
                ('2022-08-23', 900.0), # Before split
                ('2022-08-24', 903.0), # Before split
                ('2022-08-25', 301.0), # Day of split
                ('2022-08-26', 305.0)  # After split
            ],
            'AAPL': [
                ('2022-08-24', 150.0), # Unrelated stock
                ('2022-08-25', 152.0)
            ]
        }

    def test_split_adjustment_before_date(self):
        """Prices strictly before the split date should be divided by the ratio."""
        result = clean_splits(self.raw_data)
        
        # 900 / 3 = 300
        self.assertEqual(result['TSLA']['2022-08-23'], 300.0)
        self.assertEqual(result['TSLA']['2022-08-24'], 301.0)

    def test_split_preservation_after_date(self):
        """Prices on or after the split date should remain unadjusted."""
        result = clean_splits(self.raw_data)
        
        self.assertEqual(result['TSLA']['2022-08-25'], 301.0)
        self.assertEqual(result['TSLA']['2022-08-26'], 305.0)

    def test_unaffected_symbols_ignored(self):
        """Symbols not in the splits dictionary should pass through untouched."""
        result = clean_splits(self.raw_data)
        
        self.assertEqual(result['AAPL']['2022-08-24'], 150.0)
        self.assertEqual(result['AAPL']['2022-08-25'], 152.0)

    def ci_test(self):
        self.assertEqual(3, 4)

if __name__ == '__main__':
    unittest.main()