class UtilizationAnalyzer:

    def __init__(self, activities):
        self.activities = activities

    def get_driver_utilization(
        self,
        high_threshold,
        medium_threshold
    ):

        activities_by_driver = {}

        for activity in self.activities:

            if activity.timestamp is None:
                continue

            if activity.driver_id not in activities_by_driver:
                activities_by_driver[activity.driver_id] = []

            activities_by_driver[activity.driver_id].append(
                activity
            )

        results = []

        for driver_id, driver_activities in activities_by_driver.items():

            driver_activities.sort(
                key=lambda activity: activity.timestamp
            )

            online_seconds = 0
            busy_seconds = 0
            idle_seconds = 0

            online_start = None

            for i in range(len(driver_activities) - 1):

                current = driver_activities[i]
                next_activity = driver_activities[i + 1]

                current_time = current.timestamp
                next_time = next_activity.timestamp

                duration = (
                    next_time - current_time
                ).total_seconds()

                if current.status.lower() == "online":

                    if online_start is None:
                        online_start = current_time

                if online_start is not None:

                    if current.status.lower() == "busy":
                        busy_seconds += duration

                    elif current.status.lower() == "idle":
                        idle_seconds += duration

                if (
                    current.status.lower() == "offline"
                    and online_start is not None
                ):
                    online_seconds += (
                        current_time - online_start
                    ).total_seconds()

                    online_start = None

            # Close a shift if the final record is Offline.
            if driver_activities:

                last_activity = driver_activities[-1]

                if (
                    last_activity.status.lower() == "offline"
                    and online_start is not None
                ):
                    online_seconds += (
                        last_activity.timestamp - online_start
                    ).total_seconds()

            online_hours = online_seconds / 3600
            busy_hours = busy_seconds / 3600
            idle_hours = idle_seconds / 3600

            utilization = 0

            if online_hours > 0:
                utilization = (
                    busy_hours / online_hours
                ) * 100

            if utilization >= high_threshold:
                classification = "High Utilization"

            elif utilization >= medium_threshold:
                classification = "Medium Utilization"

            else:
                classification = "Low Utilization"

            results.append({
                "driver_id": driver_id,
                "online_hours": online_hours,
                "busy_hours": busy_hours,
                "idle_hours": idle_hours,
                "utilization": utilization,
                "classification": classification
            })

        return results