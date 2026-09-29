class DriverAnalyzer:

    def __init__(self, drivers, trips):
        self.drivers = drivers
        self.trips = trips

    def get_driver_analysis(self, driver_id):

        driver = None

        for item in self.drivers:
            if item.driver_id == driver_id:
                driver = item
                break

        if driver is None:
            return None

        driver_trips = []

        for trip in self.trips:
            if trip.driver_id == driver_id:
                driver_trips.append(trip)

        total_trips = len(driver_trips)

        completed_trips = 0
        cancelled_trips = 0
        revenue = 0
        total_distance = 0

        for trip in driver_trips:

            if trip.is_completed():
                completed_trips += 1
                revenue += trip.fare

            if trip.status.lower() == "cancelled":
                cancelled_trips += 1

            total_distance += trip.distance_km

        completion_rate = 0
        cancellation_rate = 0
        average_fare = 0
        average_distance = 0
        average_fare_per_km = 0

        if total_trips > 0:
            completion_rate = (
                completed_trips / total_trips
            ) * 100

            cancellation_rate = (
                cancelled_trips / total_trips
            ) * 100

        if completed_trips > 0:
            average_fare = revenue / completed_trips

            completed_distance = 0

            for trip in driver_trips:
                if trip.is_completed():
                    completed_distance += trip.distance_km

            average_distance = (
                completed_distance / completed_trips
            )

            if completed_distance > 0:
                average_fare_per_km = (
                    revenue / completed_distance
                )

        return {
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "city": driver.city,
            "rating": driver.rating,
            "status": driver.status,
            "total_trips": total_trips,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "completion_rate": completion_rate,
            "cancellation_rate": cancellation_rate,
            "revenue": revenue,
            "average_fare": average_fare,
            "average_distance": average_distance,
            "average_fare_per_km": average_fare_per_km
        }

    def get_driver_index(self):

        driver_index = {}

        for driver in self.drivers:
            driver_index[driver.driver_id] = driver

        return driver_index
    
    def get_drivers_by_completed_trips(self):
        driver_results = []

        for driver in self.drivers:

            analysis = self.get_driver_analysis(
                driver.driver_id
            )

            driver_results.append(analysis)

        driver_results.sort(
            key=lambda x: x["completed_trips"],
            reverse=True
        )

        return driver_results

    def get_drivers_by_revenue(self):

        driver_results = []

        for driver in self.drivers:

            analysis = self.get_driver_analysis(
                driver.driver_id
            )

            driver_results.append(analysis)

        driver_results.sort(
            key=lambda x: x["revenue"],
            reverse=True
        )

        return driver_results

    def get_drivers_by_cancellation_rate(self):

        driver_results = []

        for driver in self.drivers:

            analysis = self.get_driver_analysis(
                driver.driver_id
            )

            driver_results.append(analysis)

        driver_results.sort(
            key=lambda x: x["cancellation_rate"]
        )

        return driver_results