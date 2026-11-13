import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reconciliation.models import Location, SystemARecord, SystemBEntry


DATA_DIR = Path(__file__).resolve().parents[4] / "data"


def parse_amount(value):
    if value is None:
        return None

    cleaned = str(value).strip().replace(",", "")

    if not cleaned:
        return None

    try:
        amount = Decimal(cleaned)

        if not amount.is_finite():
            return None

        return amount.quantize(Decimal("0.01"))

    except (InvalidOperation, ValueError):
        return None


def normalize_reference(value):
    if value is None:
        return ""

    cleaned = re.sub(r"[\s\-_]", "", str(value).upper())

    match = re.fullmatch(r"(?:REC)?(\d+)", cleaned)

    if match:
        return f"REC-{match.group(1)}"

    return cleaned


def read_csv(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise CommandError(f"Missing CSV file: {file_path}")

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise CommandError(f"Missing CSV header: {filename}")

        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise CommandError(
                    f"Unexpected extra columns in {filename}, row {row_number}"
                )

            yield row_number, {
                key: value if value is not None else ""
                for key, value in row.items()
            }


class Command(BaseCommand):
    help = "Import the ADOSX CSV datasets into SQLite"

    @transaction.atomic
    def handle(self, *args, **options):
        locations = list(read_csv("locations.csv"))
        system_a = list(read_csv("system_a.csv"))
        system_b = list(read_csv("system_b.csv"))

        Location.objects.all().delete()
        SystemARecord.objects.all().delete()
        SystemBEntry.objects.all().delete()

        for row_number, row in locations:
            Location.objects.create(
                location_id=row["location_id"].strip(),
                org_id=row["org_id"].strip(),
                location_name=row["location_name"].strip()
            )

        for row_number, row in system_a:
            SystemARecord.objects.create(
                row_number=row_number,
                record_id=row["record_id"],
                location_id=row["location_id"],
                event_date=row["event_date"],
                category_code=row["category_code"],
                actor_id=row["actor_id"],
                base_value=row["base_value"],
                adjustment=row["adjustment"],
                total_value=row["total_value"],
                parsed_total=parse_amount(row["total_value"]),
                state=row["state"],
                raw_data=row
            )

        for row_number, row in system_b:
            SystemBEntry.objects.create(
                row_number=row_number,
                entry_id=row["entry_id"],
                record_ref=row["record_ref"],
                normalized_ref=normalize_reference(row["record_ref"]),
                location_id=row["location_id"],
                recorded_on=row["recorded_on"],
                value=row["value"],
                parsed_value=parse_amount(row["value"]),
                label=row["label"],
                raw_data=row
            )

        self.stdout.write(
            self.style.SUCCESS(
                "\nCSV IMPORT COMPLETED SUCCESSFULLY\n"
                f"Locations: {Location.objects.count()}\n"
                f"System A Records: {SystemARecord.objects.count()}\n"
                f"System B Entries: {SystemBEntry.objects.count()}"
            )
        )