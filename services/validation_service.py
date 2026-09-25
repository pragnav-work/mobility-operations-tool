import csv
from datetime import datetime


class DataValidator:

    REQUIRED_COLUMNS = {
        "drivers": [
            "driver_id",
            "driver_name",
            "city",
            "vehicle_type",
            "rating",
            "status"
        ],
        "trips": [
            "trip_id",
            "driver_id",
            "rider_id",
            "city",
            "pickup_zone",
            "drop_zone",
            "request_time",
            "pickup_time",
            "drop_time",
            "distance_km",
            "fare",
            "status",
            "cancellation_reason"
        ],
        "activities": [
            "driver_id",
            "timestamp",
            "status"
        ]
    }

    def parse_timestamp(self, value):
        if not value:
            return None

        try:
            return datetime.fromisoformat(value.strip())
        except ValueError:
            return None

    def validate_file_structure(self, file_path, file_type):
        errors = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            columns = reader.fieldnames or []

            for column in self.REQUIRED_COLUMNS[file_type]:
                if column not in columns:
                    errors.append(
                        f"{file_type}: missing required column '{column}'"
                    )

        return errors

    def validate_file(self, file_path, file_type):
        if file_type == "drivers":
            return self.validate_drivers(file_path)

        if file_type == "trips":
            return self.validate_trips(file_path)

        if file_type == "activities":
            return self.validate_activities(file_path)

        return []

    def validate_drivers(self, file_path):
        errors = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):

                required_fields = [
                    "driver_id",
                    "driver_name",
                    "city",
                    "vehicle_type",
                    "rating",
                    "status"
                ]

                for column in required_fields:
                    if not row[column].strip():
                        errors.append(
                            f"Drivers row {row_number}: missing {column}"
                        )

                if row["rating"].strip():
                    try:
                        float(row["rating"])
                    except ValueError:
                        errors.append(
                            f"Drivers row {row_number}: invalid rating"
                        )

        return errors

    def validate_trips(self, file_path):
        errors = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):

                required_fields = [
                    "trip_id",
                    "driver_id",
                    "rider_id",
                    "city",
                    "pickup_zone",
                    "drop_zone",
                    "request_time",
                    "distance_km",
                    "fare",
                    "status"
                ]

                for column in required_fields:
                    if not row[column].strip():
                        errors.append(
                            f"Trips row {row_number}: missing {column}"
                        )

                status = row["status"].strip().lower()

                # Completed trips should have pickup and drop timestamps.
                # Cancelled trips may legitimately have these fields blank.
                if status == "completed":

                    if not row["pickup_time"].strip():
                        errors.append(
                            f"Trips row {row_number}: missing pickup_time"
                        )

                    if not row["drop_time"].strip():
                        errors.append(
                            f"Trips row {row_number}: missing drop_time"
                        )

                # Cancelled trips should have a cancellation reason.
                if status == "cancelled":
                    if not row["cancellation_reason"].strip():
                        errors.append(
                            f"Trips row {row_number}: missing cancellation_reason"
                        )

                # Validate fare
                if row["fare"].strip():
                    try:
                        fare = float(row["fare"])

                        if fare < 0:
                            errors.append(
                                f"Trips row {row_number}: negative fare"
                            )

                    except ValueError:
                        errors.append(
                            f"Trips row {row_number}: invalid fare"
                        )

                # Validate distance
                if row["distance_km"].strip():
                    try:
                        distance = float(row["distance_km"])

                        if distance < 0:
                            errors.append(
                                f"Trips row {row_number}: negative distance"
                            )

                    except ValueError:
                        errors.append(
                            f"Trips row {row_number}: invalid distance"
                        )

                # Validate request timestamp
                request_time = self.parse_timestamp(
                    row["request_time"]
                )

                if row["request_time"].strip() and request_time is None:
                    errors.append(
                        f"Trips row {row_number}: invalid request timestamp"
                    )

                # Validate pickup timestamp when present
                pickup_time = self.parse_timestamp(
                    row["pickup_time"]
                )

                if row["pickup_time"].strip() and pickup_time is None:
                    errors.append(
                        f"Trips row {row_number}: invalid pickup timestamp"
                    )

                # Validate drop timestamp when present
                drop_time = self.parse_timestamp(
                    row["drop_time"]
                )

                if row["drop_time"].strip() and drop_time is None:
                    errors.append(
                        f"Trips row {row_number}: invalid drop timestamp"
                    )

                # Check trip duration when both timestamps exist
                if pickup_time and drop_time:

                    if drop_time < pickup_time:
                        errors.append(
                            f"Trips row {row_number}: invalid trip duration"
                        )

        return errors

    def validate_activities(self, file_path):
        errors = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):

                required_fields = [
                    "driver_id",
                    "timestamp",
                    "status"
                ]

                for column in required_fields:
                    if not row[column].strip():
                        errors.append(
                            f"Activities row {row_number}: missing {column}"
                        )

                timestamp = self.parse_timestamp(
                    row["timestamp"]
                )

                if row["timestamp"].strip() and timestamp is None:
                    errors.append(
                        f"Activities row {row_number}: invalid timestamp"
                    )

        return errors

    def validate_driver_ids(self, trips, drivers):
        errors = []

        driver_ids = set()

        for driver in drivers:
            driver_ids.add(driver.driver_id)

        for trip in trips:
            if trip.driver_id not in driver_ids:
                errors.append(
                    f"Trip {trip.trip_id}: invalid driver_id {trip.driver_id}"
                )

        return errors