import heapq


class ZoneAnalyzer:

    def __init__(self, trips):
        self.trips = trips

    def get_zone_analysis(
        self,
        zone_name
    ):

        total_requests = 0
        completed_trips = 0
        cancelled_trips = 0
        revenue = 0

        for trip in self.trips:

            if (
                trip.pickup_zone != zone_name
                and trip.drop_zone != zone_name
            ):
                continue

            total_requests += 1

            if trip.is_completed():

                completed_trips += 1
                revenue += trip.fare

            if trip.status.lower() == "cancelled":

                cancelled_trips += 1

        completion_rate = 0
        cancellation_rate = 0
        average_fare = 0

        if total_requests > 0:

            completion_rate = (
                completed_trips
                / total_requests
            ) * 100

            cancellation_rate = (
                cancelled_trips
                / total_requests
            ) * 100

        if completed_trips > 0:

            average_fare = (
                revenue
                / completed_trips
            )

        return {
            "zone": zone_name,
            "total_requests": total_requests,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "completion_rate": completion_rate,
            "cancellation_rate": cancellation_rate,
            "revenue": revenue,
            "average_fare": average_fare
        }

    def get_demand_distribution(
        self,
        zone_name
    ):

        distribution = {
            "06-09": 0,
            "09-12": 0,
            "12-15": 0,
            "15-18": 0,
            "18-21": 0,
            "21-00": 0
        }

        for trip in self.trips:

            if trip.pickup_zone != zone_name:
                continue

            if trip.request_time is None:
                continue

            hour = trip.request_time.hour

            if 6 <= hour < 9:
                distribution["06-09"] += 1

            elif 9 <= hour < 12:
                distribution["09-12"] += 1

            elif 12 <= hour < 15:
                distribution["12-15"] += 1

            elif 15 <= hour < 18:
                distribution["15-18"] += 1

            elif 18 <= hour < 21:
                distribution["18-21"] += 1

            elif 21 <= hour < 24:
                distribution["21-00"] += 1

        return distribution

    def get_zone_index(self, zones):

        zone_index = {}

        for zone in zones:

            zone_index[
                zone.zone_name
            ] = zone

        return zone_index

    def get_top_k_zones(
        self,
        metric,
        k
    ):

        zone_data = {}

        for trip in self.trips:

            zone = trip.pickup_zone

            if zone not in zone_data:

                zone_data[zone] = {
                    "zone": zone,
                    "demand": 0,
                    "cancellations": 0
                }

            zone_data[zone]["demand"] += 1

            if trip.status.lower() == "cancelled":

                zone_data[zone][
                    "cancellations"
                ] += 1

        zones = list(
            zone_data.values()
        )

        if metric == "demand":

            return heapq.nlargest(
                k,
                zones,
                key=lambda x: x["demand"]
            )

        if metric == "cancellation":

            return heapq.nlargest(
                k,
                zones,
                key=lambda x:
                    x["cancellations"]
            )

        return []