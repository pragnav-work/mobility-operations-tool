class Zone:
    def __init__(self, zone_name, city):
        self.zone_name = zone_name
        self.city = city

    def get_profile(self):
        return {
            "zone_name": self.zone_name,
            "city": self.city
        }