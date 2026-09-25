class Driver:
    def __init__(self, driver_id, driver_name, city, vehicle_type, rating, status):
        self.driver_id = driver_id
        self.driver_name = driver_name
        self.city = city
        self.vehicle_type = vehicle_type
        self.rating = rating
        self.status = status

    def is_active(self):
        return self.status.lower() == "active"

    def get_profile(self):
        return {
            "driver_id": self.driver_id,
            "driver_name": self.driver_name,
            "city": self.city,
            "vehicle_type": self.vehicle_type,
            "rating": self.rating,
            "status": self.status
        }
