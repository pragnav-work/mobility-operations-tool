class InsightsEngine:

    def __init__(
        self,
        zone_analyzer,
        trip_analyzer,
        cancellation_intelligence,
        utilization_results,
        anomalies
    ):
        self.zone_analyzer = zone_analyzer
        self.trip_analyzer = trip_analyzer
        self.cancellation_intelligence = (
            cancellation_intelligence
        )
        self.utilization_results = utilization_results
        self.anomalies = anomalies

    def generate_insights(self):

        insights = []

        # Highest cancellation zone
        zones = []

        zone_names = set()

        for trip in self.trip_analyzer.trips:
            zone_names.add(trip.pickup_zone)

        for zone_name in zone_names:

            analysis = self.zone_analyzer.get_zone_analysis(
                zone_name
            )

            if analysis["total_requests"] > 0:
                zones.append(analysis)

        if zones:

            zones.sort(
                key=lambda x: x["cancellation_rate"],
                reverse=True
            )

            highest_zone = zones[0]

            insights.append(
                "Zone "
                + highest_zone["zone"]
                + " has the highest cancellation rate at "
                + f"{highest_zone['cancellation_rate']:.2f}%."
            )

        # Peak demand
        peak_demand = (
            self.trip_analyzer.get_peak_demand()
        )

        if peak_demand["peak_period"]:

            insights.append(
                "The "
                + peak_demand["peak_period"]
                + " period has the highest trip demand with "
                + str(peak_demand["peak_requests"])
                + " requests."
            )

        # Low utilization
        low_utilization_count = 0

        for driver in self.utilization_results:

            if driver["utilization"] < 40:
                low_utilization_count += 1

        insights.append(
            str(low_utilization_count)
            + " drivers have utilization below 40%."
        )

        # Cancellation reason
        if self.cancellation_intelligence:

            top_reason = self.cancellation_intelligence[0]

            insights.append(
                top_reason["reason"]
                + " represents the largest cancellation category "
                + "with "
                + str(top_reason["count"])
                + " cancellations."
            )

        # Anomaly count
        insights.append(
            str(len(self.anomalies))
            + " operational anomalies have been detected."
        )

        return insights