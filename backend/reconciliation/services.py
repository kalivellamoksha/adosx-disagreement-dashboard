from collections import defaultdict

from reconciliation.models import Location, SystemARecord, SystemBEntry


def find_disagreements(org_id):
    locations = dict(
        Location.objects.values_list("location_id", "org_id")
    )

    if org_id not in set(locations.values()):
        return []

    records_a = list(SystemARecord.objects.all())
    entries_b = list(SystemBEntry.objects.all())

    records_by_id = defaultdict(list)
    entries_by_ref = defaultdict(list)

    for record in records_a:
        records_by_id[record.record_id.strip()].append(record)

    for entry in entries_b:
        entries_by_ref[entry.normalized_ref].append(entry)

    disagreements = []

    def add_issue(reason, record_id, a_value, b_value, location_id):
        disagreements.append({
            "reason": reason,
            "record_id": record_id,
            "system_a_value": str(a_value) if a_value is not None else None,
            "system_b_value": str(b_value) if b_value is not None else None,
            "location_id": location_id,
        })

    for record in records_a:
        if locations.get(record.location_id) != org_id:
            continue

        matching_entries = entries_by_ref.get(record.record_id.strip(), [])

        if not matching_entries:
            add_issue(
                "MISSING_IN_B",
                record.record_id,
                record.total_value,
                None,
                record.location_id,
            )
            continue

        own_entries = [
            entry for entry in matching_entries
            if locations.get(entry.location_id) == org_id
        ]

        cross_tenant_entries = [
            entry for entry in matching_entries
            if locations.get(entry.location_id) not in (None, org_id)
        ]

        if cross_tenant_entries:
            add_issue(
                "LOCATION_MISMATCH",
                record.record_id,
                record.total_value,
                None,
                record.location_id,
            )

        if len(own_entries) > 1:
            add_issue(
                "DUPLICATE_IN_B",
                record.record_id,
                record.total_value,
                None,
                record.location_id,
            )

        for entry in own_entries:
            if entry.location_id != record.location_id:
                add_issue(
                    "LOCATION_MISMATCH",
                    record.record_id,
                    record.total_value,
                    entry.value,
                    record.location_id,
                )

            if record.parsed_total is None or entry.parsed_value is None:
                add_issue(
                    "INVALID_VALUE",
                    record.record_id,
                    record.total_value,
                    entry.value,
                    record.location_id,
                )
            elif record.parsed_total != entry.parsed_value:
                add_issue(
                    "VALUE_MISMATCH",
                    record.record_id,
                    record.total_value,
                    entry.value,
                    record.location_id,
                )

    for entry in entries_b:
        if locations.get(entry.location_id) != org_id:
            continue

        matching_records = records_by_id.get(entry.normalized_ref, [])

        if not matching_records:
            add_issue(
                "ORPHAN_IN_B",
                entry.normalized_ref,
                None,
                entry.value,
                entry.location_id,
            )
            continue

        if all(
            locations.get(record.location_id) != org_id
            for record in matching_records
        ):
            add_issue(
                "LOCATION_MISMATCH",
                entry.normalized_ref,
                None,
                entry.value,
                entry.location_id,
            )

    return disagreements