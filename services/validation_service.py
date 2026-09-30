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

    PRIMARY_KEYS = {
        "drivers": ["driver_id"],
        "trips": ["trip_id"],
        "activities": ["driver_id", "timestamp", "status"]
    }

    def parse_timestamp(self, value):
        if not value:
            return None

        try:
            return datetime.fromisoformat(
                value.strip()
            )
        except ValueError:
            return None

    def validate_file_structure(
        self,
        file_path,
        file_type
    ):
        errors = []

        try:
            with open(file_path, "r") as file:

                reader = csv.DictReader(file)

                columns = reader.fieldnames or []

                for column in self.REQUIRED_COLUMNS[file_type]:

                    if column not in columns:

                        errors.append(
                            f"{file_type}: missing required "
                            f"column '{column}'"
                        )

                first_row = next(
                    reader,
                    None
                )

                if first_row is None:

                    errors.append(
                        f"{file_type}: file is empty"
                    )

        except (FileNotFoundError, PermissionError):

            errors.append(
                f"{file_type}: unable to read file"
            )

        return errors

    def validate_file(
        self,
        file_path,
        file_type
    ):

        if file_type == "drivers":

            errors = self.validate_drivers(
                file_path
            )

        elif file_type == "trips":

            errors = self.validate_trips(
                file_path
            )

        elif file_type == "activities":

            errors = self.validate_activities(
                file_path
            )

        else:
            return []

        errors.extend(
            self.validate_duplicates(
                file_path,
                file_type
            )
        )

        return errors

    def validate_drivers(
        self,
        file_path
    ):

        errors = []

        with open(file_path, "r") as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(
                reader,
                start=2
            ):

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
                            f"Drivers row {row_number}: "
                            f"missing {column}"
                        )

                if row["rating"].strip():

                    try:

                        rating = float(
                            row["rating"]
                        )

                        if rating < 0:

                            errors.append(
                                f"Drivers row {row_number}: "
                                f"negative rating"
                            )

                    except ValueError:

                        errors.append(
                            f"Drivers row {row_number}: "
                            f"invalid rating"
                        )

        return errors

    def validate_trips(
        self,
        file_path
    ):

        errors = []

        with open(file_path, "r") as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(
                reader,
                start=2
            ):

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
                            f"Trips row {row_number}: "
                            f"missing {column}"
                        )

                status = row["status"].strip().lower()

                if status == "completed":

                    if not row["pickup_time"].strip():

                        errors.append(
                            f"Trips row {row_number}: "
                            f"missing pickup_time"
                        )

                    if not row["drop_time"].strip():

                        errors.append(
                            f"Trips row {row_number}: "
                            f"missing drop_time"
                        )

                if status == "cancelled":

                    if not row[
                        "cancellation_reason"
                    ].strip():

                        errors.append(
                            f"Trips row {row_number}: "
                            f"missing cancellation_reason"
                        )

                if row["fare"].strip():

                    try:

                        fare = float(
                            row["fare"]
                        )

                        if fare < 0:

                            errors.append(
                                f"Trips row {row_number}: "
                                f"negative fare"
                            )

                    except ValueError:

                        errors.append(
                            f"Trips row {row_number}: "
                            f"invalid fare"
                        )

                if row["distance_km"].strip():

                    try:

                        distance = float(
                            row["distance_km"]
                        )

                        if distance <= 0:

                            errors.append(
                                f"Trips row {row_number}: "
                                f"distance must be greater than zero"
                            )

                    except ValueError:

                        errors.append(
                            f"Trips row {row_number}: "
                            f"invalid distance"
                        )

                request_time = (
                    self.parse_timestamp(
                        row["request_time"]
                    )
                )

                if (
                    row["request_time"].strip()
                    and request_time is None
                ):

                    errors.append(
                        f"Trips row {row_number}: "
                        f"invalid request timestamp"
                    )

                pickup_time = (
                    self.parse_timestamp(
                        row["pickup_time"]
                    )
                )

                if (
                    row["pickup_time"].strip()
                    and pickup_time is None
                ):

                    errors.append(
                        f"Trips row {row_number}: "
                        f"invalid pickup timestamp"
                    )

                drop_time = (
                    self.parse_timestamp(
                        row["drop_time"]
                    )
                )

                if (
                    row["drop_time"].strip()
                    and drop_time is None
                ):

                    errors.append(
                        f"Trips row {row_number}: "
                        f"invalid drop timestamp"
                    )

                if pickup_time and drop_time:

                    if drop_time < pickup_time:

                        errors.append(
                            f"Trips row {row_number}: "
                            f"invalid trip duration"
                        )

        return errors

    def validate_activities(
        self,
        file_path
    ):

        errors = []

        with open(file_path, "r") as file:

            reader = csv.DictReader(file)

            for row_number, row in enumerate(
                reader,
                start=2
            ):

                required_fields = [
                    "driver_id",
                    "timestamp",
                    "status"
                ]

                for column in required_fields:

                    if not row[column].strip():

                        errors.append(
                            f"Activities row {row_number}: "
                            f"missing {column}"
                        )

                timestamp = (
                    self.parse_timestamp(
                        row["timestamp"]
                    )
                )

                if (
                    row["timestamp"].strip()
                    and timestamp is None
                ):

                    errors.append(
                        f"Activities row {row_number}: "
                        f"invalid timestamp"
                    )

        return errors

    def validate_duplicates(
        self,
        file_path,
        file_type
    ):

        errors = []

        primary_keys = self.PRIMARY_KEYS.get(
            file_type
        )

        if not primary_keys:
            return errors

        with open(file_path, "r") as file:

            reader = csv.DictReader(file)

            seen = set()

            for row_number, row in enumerate(
                reader,
                start=2
            ):

                key = tuple(
                    row[column].strip()
                    for column in primary_keys
                )

                if key in seen:

                    errors.append(
                        f"{file_type} row {row_number}: "
                        f"duplicate record"
                    )

                seen.add(key)

        return errors

    def validate_driver_ids(
        self,
        trips,
        drivers
    ):

        errors = []

        driver_ids = {
            driver.driver_id
            for driver in drivers
        }

        for trip in trips:

            if trip.driver_id not in driver_ids:

                errors.append(
                    f"Trip {trip.trip_id}: "
                    f"invalid driver_id "
                    f"{trip.driver_id}"
                )

        return errors