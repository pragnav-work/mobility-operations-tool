import heapq
class TripAnalyzer:

    def __init__(self, trips):
        self.trips = trips

    def get_total_trips(self):
        return len(self.trips)

    def get_completed_trips(self):

        count = 0

        for trip in self.trips:
            if trip.is_completed():
                count += 1

        return count

    def get_cancelled_trips(self):

        count = 0

        for trip in self.trips:
            if trip.status.lower() == "cancelled":
                count += 1

        return count

    def get_total_revenue(self):

        revenue = 0

        for trip in self.trips:
            if trip.is_completed():
                revenue += trip.fare

        return revenue

    def get_average_fare(self):

        completed_trips = []

        for trip in self.trips:
            if trip.is_completed():
                completed_trips.append(trip)

        if not completed_trips:
            return 0

        total_fare = 0

        for trip in completed_trips:
            total_fare += trip.fare

        return total_fare / len(completed_trips)

    def get_average_distance(self):

        if not self.trips:
            return 0

        total_distance = 0

        for trip in self.trips:
            total_distance += trip.distance_km

        return total_distance / len(self.trips)

    def get_average_duration(self):

        durations = []

        for trip in self.trips:

            duration = trip.calculate_duration()

            if duration is not None:
                durations.append(duration)

        if not durations:
            return 0

        total_seconds = 0

        for duration in durations:
            total_seconds += duration.total_seconds()

        return total_seconds / len(durations) / 60

    def get_status_frequency(self):

        frequency = {}

        for trip in self.trips:

            status = trip.status

            if status not in frequency:
                frequency[status] = 0

            frequency[status] += 1

        return frequency

    def get_cancellation_reason_frequency(self):

        frequency = {}

        for trip in self.trips:

            if trip.status.lower() == "cancelled":

                reason = trip.cancellation_reason

                if reason not in frequency:
                    frequency[reason] = 0

                frequency[reason] += 1

        return frequency

    def get_trip_index(self):

        trip_index = {}

        for trip in self.trips:
            trip_index[trip.trip_id] = trip

        return trip_index

    def get_top_k_riders(self, k):

        rider_frequency = {}

        for trip in self.trips:

            rider_id = trip.rider_id

            if rider_id not in rider_frequency:
                rider_frequency[rider_id] = 0

            rider_frequency[rider_id] += 1

        riders = []

        for rider_id, trip_count in rider_frequency.items():

            riders.append({
                "rider_id": rider_id,
                "trip_count": trip_count
            })

        return heapq.nlargest(
            k,
            riders,
            key=lambda x: x["trip_count"]
        )

    def get_idle_time_analysis(self, threshold_minutes):

        trips_by_driver = {}

        for trip in self.trips:

            if trip.pickup_time is None or trip.drop_time is None:
                continue

            if trip.driver_id not in trips_by_driver:
                trips_by_driver[trip.driver_id] = []

            trips_by_driver[trip.driver_id].append(trip)

        idle_periods = []

        for driver_id, driver_trips in trips_by_driver.items():

            driver_trips.sort(
                key=lambda trip: trip.pickup_time
            )

            for i in range(len(driver_trips) - 1):

                previous_trip = driver_trips[i]
                next_trip = driver_trips[i + 1]

                idle_time = (
                    next_trip.pickup_time -
                    previous_trip.drop_time
                )

                idle_minutes = (
                    idle_time.total_seconds() / 60
                )

                if idle_minutes >= threshold_minutes:

                    idle_periods.append({
                        "driver_id": driver_id,
                        "previous_trip": previous_trip.trip_id,
                        "next_trip": next_trip.trip_id,
                        "idle_minutes": idle_minutes
                    })

        return idle_periods

    def get_peak_demand(self):

        demand = {
            "06-09": 0,
            "09-12": 0,
            "12-15": 0,
            "15-18": 0,
            "18-21": 0,
            "21-00": 0
        }

        for trip in self.trips:

            if trip.request_time is None:
                continue

            hour = trip.request_time.hour

            if 6 <= hour < 9:
                demand["06-09"] += 1

            elif 9 <= hour < 12:
                demand["09-12"] += 1

            elif 12 <= hour < 15:
                demand["12-15"] += 1

            elif 15 <= hour < 18:
                demand["15-18"] += 1

            elif 18 <= hour < 21:
                demand["18-21"] += 1

            elif 21 <= hour < 24:
                demand["21-00"] += 1

        peak_period = None
        peak_requests = 0

        for time_slot, requests in demand.items():

            if requests > peak_requests:
                peak_period = time_slot
                peak_requests = requests

        return {
            "demand": demand,
            "peak_period": peak_period,
            "peak_requests": peak_requests
        }
    
    def get_cancellation_intelligence(self):

        reason_frequency = {}

        for trip in self.trips:

            if trip.status.lower() != "cancelled":
                continue

            reason = trip.cancellation_reason

            if reason not in reason_frequency:
                reason_frequency[reason] = 0

            reason_frequency[reason] += 1

        cancellation_results = []

        for reason, count in reason_frequency.items():

            cancellation_results.append({
                "reason": reason,
                "count": count
            })

        cancellation_results.sort(
            key=lambda x: x["count"],
            reverse=True
        )

        total_cancellations = 0

        for item in cancellation_results:
            total_cancellations += item["count"]

        for item in cancellation_results:

            if total_cancellations > 0:
                item["percentage"] = (
                    item["count"] /
                    total_cancellations
                ) * 100
            else:
                item["percentage"] = 0

        return cancellation_results