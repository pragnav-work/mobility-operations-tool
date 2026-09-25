class DriverActivity:
    def __init__(self, driver_id, timestamp, status):
        self.driver_id = driver_id
        self.timestamp = timestamp
        self.status = status

    def get_profile(self):
        return {
            "driver_id": self.driver_id,
            "timestamp": self.timestamp,
            "status": self.status
        }