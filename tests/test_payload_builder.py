import unittest

from src.sim_boq_demo.payload_builder import build_payload, calculate_totals


class PayloadBuilderTests(unittest.TestCase):
    def test_calculate_totals_splits_analysis_and_devices(self):
        rows = [
            {"quantity": 10, "price": 5, "is_device": False},
            {"quantity": 2, "price": 20, "is_device": True},
        ]

        totals = calculate_totals(rows, reserve_fund_rate=5)

        self.assertEqual(totals["sum_analyse"], 50)
        self.assertEqual(totals["sum_reserve_fund"], 2.5)
        self.assertEqual(totals["total_without_vat"], 52.5)
        self.assertEqual(totals["vat"], 10.5)
        self.assertEqual(totals["sum_device_without_vat"], 40)
        self.assertEqual(totals["sum_device"], 48)

    def test_build_payload_creates_groups_and_details(self):
        header = {"construction": "Demo", "reserve_fund_rate": 5}
        rows = [
            {
                "code": "A-001",
                "name": "Earthworks",
                "unit": "m3",
                "quantity": 3,
                "price": 10,
                "product_id": 1,
                "unit_id": 1,
                "group_id": 10,
                "group_name": "Earthworks",
                "is_device": False,
                "is_custom": False,
                "note": "",
            }
        ]

        payload = build_payload(header, rows)

        self.assertEqual(len(payload["groups"]), 1)
        self.assertEqual(len(payload["details"]), 1)
        self.assertEqual(payload["details"][0]["detail_type"], "analyse_in_list")
        self.assertEqual(payload["details"][0]["total"], 30)


if __name__ == "__main__":
    unittest.main()

