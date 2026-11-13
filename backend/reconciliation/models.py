from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=50, primary_key=True)
    org_id = models.CharField(max_length=50, db_index=True)
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.location_id} - {self.org_id}"


class SystemARecord(models.Model):
    row_number = models.PositiveIntegerField(unique=True)
    record_id = models.CharField(max_length=100, db_index=True)
    location_id = models.CharField(max_length=100)
    event_date = models.CharField(max_length=100, blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    actor_id = models.CharField(max_length=100, blank=True)
    base_value = models.CharField(max_length=100, blank=True)
    adjustment = models.CharField(max_length=100, blank=True)
    total_value = models.CharField(max_length=100, blank=True)

    parsed_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )

    state = models.CharField(max_length=100, blank=True)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    row_number = models.PositiveIntegerField(unique=True)
    entry_id = models.CharField(max_length=100, db_index=True)
    record_ref = models.CharField(max_length=100, blank=True)

    normalized_ref = models.CharField(
        max_length=100,
        blank=True,
        db_index=True
    )

    location_id = models.CharField(max_length=100)
    recorded_on = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=100, blank=True)

    parsed_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True
    )

    label = models.CharField(max_length=100, blank=True)
    raw_data = models.JSONField(default=dict)

    def __str__(self):
        return self.entry_id