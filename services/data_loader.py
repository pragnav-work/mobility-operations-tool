import csv
from datetime import datetime

from models.driver import Driver
from models.trip import Trip
from models.zone import Zone
from models.activity import DriverActivity


class DataLoader:

    def parse_timestamp(self, value):
        if not value:
            return None

        try:
            return datetime.fromisoformat(value.strip())
        except ValueError:
            return None

    def parse_float(self, value):
        if not value:
            return 0

        try:
            return float(value)
        except ValueError:
            return 0

    def load_drivers(self, file_path):
        drivers = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:

                driver = Driver(
                    row["driver_id"],
                    row["driver_name"],
                    row["city"],
                    row["vehicle_type"],
                    self.parse_float(row["rating"]),
                    row["status"]
                )

                drivers.append(driver)

        return drivers

    def load_trips(self, file_path):
        trips = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:

                trip = Trip(
                    row["trip_id"],
                    row["driver_id"],
                    row["rider_id"],
                    row["city"],
                    row["pickup_zone"],
                    row["drop_zone"],
                    self.parse_timestamp(row["request_time"]),
                    self.parse_timestamp(row["pickup_time"]),
                    self.parse_timestamp(row["drop_time"]),
                    self.parse_float(row["distance_km"]),
                    self.parse_float(row["fare"]),
                    row["status"],
                    row["cancellation_reason"]
                )

                trips.append(trip)

        return trips

    def load_activities(self, file_path):
        activities = []

        with open(file_path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:

                activity = DriverActivity(
                    row["driver_id"],
                    self.parse_timestamp(row["timestamp"]),
                    row["status"]
                )

                activities.append(activity)

        return activities

    def load_zones(self, trips):
        zones = {}

        for trip in trips:

            if trip.pickup_zone not in zones:
                zones[trip.pickup_zone] = Zone(
                    trip.pickup_zone,
                    trip.city
                )

            if trip.drop_zone not in zones:
                zones[trip.drop_zone] = Zone(
                    trip.drop_zone,
                    trip.city
                )

        return list(zones.values())