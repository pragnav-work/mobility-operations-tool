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