import csv
import os
import tempfile
import unittest

from datetime import datetime

from models.driver import Driver
from models.trip import Trip

from services.validation_service import (
    DataValidator
)

from services.trip_analyzer import (
    TripAnalyzer
)


class TestDataValidation(unittest.TestCase):

    def setUp(self):

        self.validator = DataValidator()

        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):

        self.temp_dir.cleanup()

    def create_file(
        self,
        filename,
        content
    ):

        path = os.path.join(
            self.temp_dir.name,
            filename
        )

        with open(
            path,
            "w"
        ) as file:

            file.write(content)

        return path

    def test_empty_file(self):

        path = self.create_file(
            "empty.csv",
            ""
        )

        errors = (
            self.validator
            .validate_file_structure(
                path,
                "drivers"
            )
        )

        self.assertTrue(
            any(
                "empty" in error.lower()
                for error in errors
            )
        )

    def test_missing_column(self):

        content = (
            "driver_id,driver_name,city\n"
            "D001,Asha,Bangalore\n"
        )

        path = self.create_file(
            "missing.csv",
            content
        )

        errors = (
            self.validator
            .validate_file_structure(
                path,
                "drivers"
            )
        )

        self.assertTrue(
            any(
                "vehicle_type" in error
                for error in errors
            )
        )

    def test_duplicate_driver(self):

        content = (
            "driver_id,driver_name,city,"
            "vehicle_type,rating,status\n"
            "D001,Asha,Bangalore,Car,4.5,Active\n"
            "D001,Ravi,Bangalore,Bike,4.2,Active\n"
        )

        path = self.create_file(
            "duplicates.csv",
            content
        )

        errors = (
            self.validator
            .validate_duplicates(
                path,
                "drivers"
            )
        )

        self.assertEqual(
            len(errors),
            1
        )

        self.assertIn(
            "duplicate",
            errors[0].lower()
        )

    def test_negative_fare(self):

        content = (
            "trip_id,driver_id,rider_id,city,"
            "pickup_zone,drop_zone,request_time,"
            "pickup_time,drop_time,distance_km,"
            "fare,status,cancellation_reason\n"
            "T001,D001,R001,Bangalore,Z01,Z02,"
            "2026-01-01T10:00:00,"
            "2026-01-01T10:05:00,"
            "2026-01-01T10:20:00,"
            "5,-100,Completed,\n"
        )

        path = self.create_file(
            "negative_fare.csv",
            content
        )

        errors = (
            self.validator
            .validate_trips(path)
        )

        self.assertTrue(
            any(
                "negative fare" in error.lower()
                for error in errors
            )
        )

    def test_invalid_timestamp(self):

        content = (
            "trip_id,driver_id,rider_id,city,"
            "pickup_zone,drop_zone,request_time,"
            "pickup_time,drop_time,distance_km,"
            "fare,status,cancellation_reason\n"
            "T001,D001,R001,Bangalore,Z01,Z02,"
            "not-a-date,"
            "2026-01-01T10:05:00,"
            "2026-01-01T10:20:00,"
            "5,100,Completed,\n"
        )

        path = self.create_file(
            "invalid_timestamp.csv",
            content
        )

        errors = (
            self.validator
            .validate_trips(path)
        )

        self.assertTrue(
            any(
                "invalid request timestamp"
                in error.lower()
                for error in errors
            )
        )

    def test_invalid_driver_id(self):

        driver = Driver(
            "D001",
            "Asha",
            "Bangalore",
            "Car",
            4.5,
            "Active"
        )

        trip = Trip(
            "T001",
            "D999",
            "R001",
            "Bangalore",
            "Z01",
            "Z02",
            datetime(2026, 1, 1, 10, 0),
            datetime(2026, 1, 1, 10, 5),
            datetime(2026, 1, 1, 10, 20),
            5,
            100,
            "Completed",
            ""
        )

        errors = (
            self.validator
            .validate_driver_ids(
                [trip],
                [driver]
            )
        )

        self.assertEqual(
            len(errors),
            1
        )

        self.assertIn(
            "D999",
            errors[0]
        )


class TestTripAnalyzer(unittest.TestCase):

    def setUp(self):

        self.trips = [

            Trip(
                "T001",
                "D001",
                "R001",
                "Bangalore",
                "Z01",
                "Z02",
                datetime(2026, 1, 1, 10, 0),
                datetime(2026, 1, 1, 10, 5),
                datetime(2026, 1, 1, 10, 20),
                5,
                100,
                "Completed",
                ""
            ),

            Trip(
                "T002",
                "D001",
                "R002",
                "Bangalore",
                "Z01",
                "Z03",
                datetime(2026, 1, 1, 11, 0),
                None,
                None,
                3,
                0,
                "Cancelled",
                "Driver cancelled"
            )
        ]

        self.analyzer = TripAnalyzer(
            self.trips
        )

    def test_total_trips(self):

        self.assertEqual(
            self.analyzer.get_total_trips(),
            2
        )

    def test_completed_trips(self):

        self.assertEqual(
            self.analyzer.get_completed_trips(),
            1
        )

    def test_cancelled_trips(self):

        self.assertEqual(
            self.analyzer.get_cancelled_trips(),
            1
        )

    def test_average_fare(self):

        self.assertEqual(
            self.analyzer.get_average_fare(),
            100
        )

    def test_status_frequency(self):

        result = (
            self.analyzer
            .get_status_frequency()
        )

        self.assertEqual(
            result["Completed"],
            1
        )

        self.assertEqual(
            result["Cancelled"],
            1
        )

    def test_cancellation_intelligence(self):

        result = (
            self.analyzer
            .get_cancellation_intelligence()
        )

        self.assertEqual(
            result[0]["count"],
            1
        )

        self.assertEqual(
            result[0]["percentage"],
            100
        )


if __name__ == "__main__":
    unittest.main()