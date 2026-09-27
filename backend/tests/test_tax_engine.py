import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from tax_engine import TAX_RULES, calculate_tax, classify_transaction, process_invoice_tax


class ClassifyTransactionTests(unittest.TestCase):
    def test_matches_keyword_case_insensitively(self):
        self.assertEqual(classify_transaction("Legal CONSULTING fee"), "professional_services")
        self.assertEqual(classify_transaction("Monthly office rent"), "rent")
        self.assertEqual(classify_transaction("Courier charges"), "transport")

    def test_unknown_description_falls_back_to_other(self):
        self.assertEqual(classify_transaction("Miscellaneous"), "other")
        self.assertEqual(classify_transaction(""), "other")


class CalculateTaxTests(unittest.TestCase):
    def test_filer_rate(self):
        result = calculate_tax(10000, "rent", is_filer=True)
        self.assertEqual(result["withholding_tax"], 1500.0)
        self.assertEqual(result["amount_after_tax"], 8500.0)
        self.assertEqual(result["section"], "155")
        self.assertEqual(result["taxpayer_status"], "Filer")

    def test_non_filer_rate(self):
        result = calculate_tax(10000, "rent", is_filer=False)
        self.assertEqual(result["withholding_tax"], 3000.0)
        self.assertEqual(result["taxpayer_status"], "Non-Filer")

    def test_unknown_type_uses_other_rule(self):
        result = calculate_tax(1000, "not_a_category")
        self.assertEqual(result["withholding_tax"], 1000 * TAX_RULES["other"]["rate_filer"])

    def test_rounds_to_two_decimals(self):
        result = calculate_tax(123.456, "supply_of_goods")
        self.assertEqual(result["withholding_tax"], 4.94)


class ProcessInvoiceTaxTests(unittest.TestCase):
    def test_classifies_and_calculates(self):
        result = process_invoice_tax({"description": "Freight to Lahore", "total_amount": "5000"})
        self.assertEqual(result["transaction_type"], "transport")
        self.assertEqual(result["withholding_tax"], 100.0)

    def test_invalid_or_missing_amount_is_zero(self):
        for data in ({"total_amount": "N/A"}, {"total_amount": None}, {}):
            result = process_invoice_tax(data)
            self.assertEqual(result["amount"], 0.0)
            self.assertEqual(result["withholding_tax"], 0.0)


if __name__ == "__main__":
    unittest.main()
