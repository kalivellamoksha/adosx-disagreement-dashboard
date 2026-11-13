from decimal import Decimal

from django.test import TestCase, override_settings

from reconciliation.models import Location, SystemARecord, SystemBEntry
from reconciliation.services import find_disagreements


class DisagreementTests(TestCase):

    def setUp(self):
        Location.objects.create(
            location_id="LOC-101",
            org_id="ORG-A",
            location_name="Location 101"
        )

        Location.objects.create(
            location_id="LOC-201",
            org_id="ORG-B",
            location_name="Location 201"
        )

    def create_a(self, row_number, record_id, value, location="LOC-101"):
        return SystemARecord.objects.create(
            row_number=row_number,
            record_id=record_id,
            location_id=location,
            total_value=str(value),
            parsed_total=Decimal(str(value)),
        )

    def create_b(
        self,
        row_number,
        entry_id,
        record_ref,
        value,
        location="LOC-101"
    ):
        return SystemBEntry.objects.create(
            row_number=row_number,
            entry_id=entry_id,
            record_ref=record_ref,
            normalized_ref=record_ref,
            location_id=location,
            value=str(value),
            parsed_value=Decimal(str(value)),
        )

    def test_missing_in_b(self):
        self.create_a(1, "REC-1001", 500)

        issues = find_disagreements("ORG-A")

        self.assertTrue(
            any(issue["reason"] == "MISSING_IN_B" for issue in issues)
        )

    def test_orphan_in_b(self):
        self.create_b(1, "ENT-1", "REC-9999", 500)

        issues = find_disagreements("ORG-A")

        self.assertTrue(
            any(issue["reason"] == "ORPHAN_IN_B" for issue in issues)
        )

    def test_duplicate_in_b(self):
        self.create_a(1, "REC-1001", 500)

        self.create_b(1, "ENT-1", "REC-1001", 500)
        self.create_b(2, "ENT-2", "REC-1001", 500)

        issues = find_disagreements("ORG-A")

        self.assertTrue(
            any(issue["reason"] == "DUPLICATE_IN_B" for issue in issues)
        )

    def test_value_mismatch(self):
        self.create_a(1, "REC-1001", 500)
        self.create_b(1, "ENT-1", "REC-1001", 700)

        issues = find_disagreements("ORG-A")

        self.assertTrue(
            any(issue["reason"] == "VALUE_MISMATCH" for issue in issues)
        )

    def test_matching_values_not_flagged(self):
        self.create_a(1, "REC-1001", 500)
        self.create_b(1, "ENT-1", "REC-1001", 500)

        issues = find_disagreements("ORG-A")

        self.assertEqual(issues, [])

    def test_tenant_isolation(self):
        self.create_a(1, "REC-1001", 500, "LOC-101")
        self.create_a(2, "REC-2001", 700, "LOC-201")

        issues = find_disagreements("ORG-A")

        record_ids = [issue["record_id"] for issue in issues]

        self.assertIn("REC-1001", record_ids)
        self.assertNotIn("REC-2001", record_ids)

    @override_settings(ADOSX_TENANT_ID="ORG-A")
    def test_api_blocks_other_tenant(self):
        response = self.client.get(
            "/api/disagreements/",
            {"org_id": "ORG-B"}
        )

        self.assertEqual(response.status_code, 403)

    @override_settings(ADOSX_TENANT_ID="ORG-A")
    def test_api_allows_current_tenant(self):
        response = self.client.get(
            "/api/disagreements/",
            {"org_id": "ORG-A"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["org_id"],
            "ORG-A"
        )

    @override_settings(ADOSX_TENANT_ID="ORG-A")
    def test_api_defaults_to_server_tenant(self):
        response = self.client.get("/api/disagreements/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["org_id"],
            "ORG-A"
        )

    @override_settings(ADOSX_TENANT_ID="ORG-A")
    def test_api_does_not_return_other_tenant_records(self):
        self.create_a(1, "REC-1001", 500, "LOC-101")
        self.create_a(2, "REC-2001", 700, "LOC-201")

        response = self.client.get("/api/disagreements/")

        self.assertEqual(response.status_code, 200)

        record_ids = [
            issue["record_id"]
            for issue in response.json()["disagreements"]
        ]

        self.assertIn("REC-1001", record_ids)
        self.assertNotIn("REC-2001", record_ids)

    @override_settings(ADOSX_TENANT_ID="ORG-A")
    def test_cross_tenant_reference_does_not_leak_value(self):
        self.create_a(
            1,
            "REC-1001",
            500,
            "LOC-101"
        )

        self.create_b(
            1,
            "ENT-1",
            "REC-1001",
            999999,
            "LOC-201"
        )

        response = self.client.get("/api/disagreements/")

        self.assertEqual(response.status_code, 200)

        issues = response.json()["disagreements"]

        self.assertTrue(
            any(
                issue["reason"] == "LOCATION_MISMATCH"
                for issue in issues
            )
        )

        for issue in issues:
            self.assertNotEqual(
                issue["system_b_value"],
                "999999"
            )

        self.assertNotIn(
            "LOC-201",
            [issue["location_id"] for issue in issues]
        )