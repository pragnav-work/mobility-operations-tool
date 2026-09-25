class Trip:
    def __init__(
        self,
        trip_id,
        driver_id,
        rider_id,
        city,
        pickup_zone,
        drop_zone,
        request_time,
        pickup_time,
        drop_time,
        distance_km,
        fare,
        status,
        cancellation_reason
    ):
        self.trip_id = trip_id
        self.driver_id = driver_id
        self.rider_id = rider_id
        self.city = city
        self.pickup_zone = pickup_zone
        self.drop_zone = drop_zone
        self.request_time = request_time
        self.pickup_time = pickup_time
        self.drop_time = drop_time
        self.distance_km = distance_km
        self.fare = fare
        self.status = status
        self.cancellation_reason = cancellation_reason

    def is_completed(self):
        return self.status.lower() == "completed"

    def calculate_duration(self):
        if self.pickup_time and self.drop_time:
            return self.drop_time - self.pickup_time
        return None

    def calculate_fare_per_km(self):
        if self.distance_km > 0:
            return self.fare / self.distance_km
        return None