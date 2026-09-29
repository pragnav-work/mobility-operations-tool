class AnomalyDetector:

    def __init__(self, drivers, trips, utilization_results):
        self.drivers = drivers
        self.trips = trips
        self.utilization_results = utilization_results

    def detect_trip_anomalies(
        self,
        long_duration_minutes,
        unusual_fare_multiplier
    ):

        anomalies = []

        driver_ids = set()

        for driver in self.drivers:
            driver_ids.add(driver.driver_id)

        completed_fares = []

        for trip in self.trips:
            if trip.is_completed() and trip.fare > 0:
                completed_fares.append(trip.fare)

        average_fare = 0

        if completed_fares:
            average_fare = (
                sum(completed_fares) /
                len(completed_fares)
            )

        unusual_fare_threshold = (
            average_fare * unusual_fare_multiplier
        )

        for trip in self.trips:

            if trip.fare < 0:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Negative fare"
                })

            if trip.distance_km == 0:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Zero distance"
                })

            if trip.driver_id not in driver_ids:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Unknown driver"
                })

            if trip.request_time is None:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Invalid request timestamp"
                })

            if trip.pickup_time is not None and trip.drop_time is not None:

                duration = trip.calculate_duration()

                if duration is not None:

                    duration_minutes = (
                        duration.total_seconds() / 60
                    )

                    if duration_minutes < 0:
                        anomalies.append({
                            "type": "Trip",
                            "id": trip.trip_id,
                            "issue": "Drop time before pickup time"
                        })

                    elif duration_minutes > long_duration_minutes:
                        anomalies.append({
                            "type": "Trip",
                            "id": trip.trip_id,
                            "issue": "Extremely long trip duration"
                        })

            if (
                average_fare > 0
                and trip.fare > unusual_fare_threshold
            ):
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Unusually high fare"
                })

        return anomalies

    def detect_driver_anomalies(
        self,
        high_cancellation_threshold,
        low_utilization_threshold,
        high_trip_count_threshold,
        low_rating_threshold
    ):

        anomalies = []

        trips_by_driver = {}

        for trip in self.trips:

            if trip.driver_id not in trips_by_driver:
                trips_by_driver[trip.driver_id] = []

            trips_by_driver[trip.driver_id].append(trip)

        utilization_by_driver = {}

        for result in self.utilization_results:
            utilization_by_driver[
                result["driver_id"]
            ] = result["utilization"]

        for driver in self.drivers:

            driver_trips = trips_by_driver.get(
                driver.driver_id,
                []
            )

            total_trips = len(driver_trips)

            cancelled_trips = 0

            for trip in driver_trips:
                if trip.status.lower() == "cancelled":
                    cancelled_trips += 1

            cancellation_rate = 0

            if total_trips > 0:
                cancellation_rate = (
                    cancelled_trips /
                    total_trips
                ) * 100

            if cancellation_rate > high_cancellation_threshold:
                anomalies.append({
                    "type": "Driver",
                    "id": driver.driver_id,
                    "issue": "High cancellation rate"
                })

            utilization = utilization_by_driver.get(
                driver.driver_id
            )

            if (
                utilization is not None
                and utilization < low_utilization_threshold
            ):
                anomalies.append({
                    "type": "Driver",
                    "id": driver.driver_id,
                    "issue": "Low utilization"
                })

            if total_trips > high_trip_count_threshold:
                anomalies.append({
                    "type": "Driver",
                    "id": driver.driver_id,
                    "issue": "Unusually high trip count"
                })

            if driver.rating < low_rating_threshold:
                anomalies.append({
                    "type": "Driver",
                    "id": driver.driver_id,
                    "issue": "Low rating"
                })

        return anomalies

    def get_all_anomalies(
        self,
        long_duration_minutes=180,
        unusual_fare_multiplier=3,
        high_cancellation_threshold=30,
        low_utilization_threshold=40,
        high_trip_count_threshold=40,
        low_rating_threshold=3.5
    ):

        trip_anomalies = self.detect_trip_anomalies(
            long_duration_minutes,
            unusual_fare_multiplier
        )

        driver_anomalies = self.detect_driver_anomalies(
            high_cancellation_threshold,
            low_utilization_threshold,
            high_trip_count_threshold,
            low_rating_threshold
        )

        return trip_anomalies + driver_anomalies