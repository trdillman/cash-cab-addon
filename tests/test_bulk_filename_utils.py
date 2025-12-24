import unittest


class TestBulkFilenameUtils(unittest.TestCase):
    def test_address_only_drops_leading_venue_segment(self):
        from bulk.filename_utils import address_only

        self.assertEqual(
            address_only("Starbucks, 123 Main St, Toronto"),
            "123 Main St, Toronto",
        )

    def test_address_only_drops_leading_venue_prefix_before_number(self):
        from bulk.filename_utils import address_only

        self.assertEqual(
            address_only("Starbucks - 123 Main St, Toronto"),
            "123 Main St, Toronto",
        )

    def test_address_only_keeps_normal_address(self):
        from bulk.filename_utils import address_only

        self.assertEqual(
            address_only("1600 Pennsylvania Ave NW, Washington, DC"),
            "1600 Pennsylvania Ave NW, Washington, DC",
        )


if __name__ == "__main__":
    unittest.main()

