import os

from flask import Flask, render_template, request

from services.data_loader import DataLoader
from services.validation_service import DataValidator
from services.driver_analyzer import DriverAnalyzer
from services.trip_analyzer import TripAnalyzer
from services.zone_analyzer import ZoneAnalyzer


app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

loader = DataLoader()
validator = DataValidator()

drivers = []
trips = []
activities = []
zones = []

driver_analyzer = None
trip_analyzer = None
zone_analyzer = None

driver_index = {}
trip_index = {}
zone_index = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():

    global drivers
    global trips
    global activities
    global zones
    global driver_analyzer
    global trip_analyzer
    global zone_analyzer
    global driver_index
    global trip_index
    global zone_index

    drivers_file = request.files.get("drivers")
    trips_file = request.files.get("trips")
    activities_file = request.files.get("activities")

    if not drivers_file or not trips_file or not activities_file:
        return render_template(
            "index.html",
            errors=["Please upload all three CSV files."]
        )

    drivers_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "drivers.csv"
    )

    trips_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "trips.csv"
    )

    activities_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "driver_activity.csv"
    )

    drivers_file.save(drivers_path)
    trips_file.save(trips_path)
    activities_file.save(activities_path)

    structure_errors = []

    structure_errors.extend(
        validator.validate_file_structure(
            drivers_path,
            "drivers"
        )
    )

    structure_errors.extend(
        validator.validate_file_structure(
            trips_path,
            "trips"
        )
    )

    structure_errors.extend(
        validator.validate_file_structure(
            activities_path,
            "activities"
        )
    )

    if structure_errors:
        return render_template(
            "index.html",
            errors=structure_errors
        )

    validation_errors = []

    validation_errors.extend(
        validator.validate_file(
            drivers_path,
            "drivers"
        )
    )

    validation_errors.extend(
        validator.validate_file(
            trips_path,
            "trips"
        )
    )

    validation_errors.extend(
        validator.validate_file(
            activities_path,
            "activities"
        )
    )

    drivers = loader.load_drivers(drivers_path)
    trips = loader.load_trips(trips_path)
    activities = loader.load_activities(activities_path)

    validation_errors.extend(
        validator.validate_driver_ids(
            trips,
            drivers
        )
    )

    zones = loader.load_zones(trips)

    # Create analyzers.
    driver_analyzer = DriverAnalyzer(
        drivers,
        trips
    )

    trip_analyzer = TripAnalyzer(trips)

    zone_analyzer = ZoneAnalyzer(trips)

    # Create dictionary indexes for search.
    driver_index = driver_analyzer.get_driver_index()

    trip_index = trip_analyzer.get_trip_index()

    zone_index = zone_analyzer.get_zone_index(zones)

    summary = {
        "drivers": len(drivers),
        "trips": len(trips),
        "activities": len(activities),
        "zones": len(zones)
    }

    trip_summary = {
        "total_trips": trip_analyzer.get_total_trips(),
        "completed_trips": trip_analyzer.get_completed_trips(),
        "cancelled_trips": trip_analyzer.get_cancelled_trips(),
        "total_revenue": trip_analyzer.get_total_revenue(),
        "average_fare": trip_analyzer.get_average_fare(),
        "average_distance": trip_analyzer.get_average_distance(),
        "average_duration": trip_analyzer.get_average_duration()
    }

    return render_template(
        "dashboard.html",
        summary=summary,
        trip_summary=trip_summary,
        errors=validation_errors
    )


@app.route("/driver", methods=["GET", "POST"])
def driver_analysis():

    if driver_analyzer is None:
        return render_template(
            "index.html",
            errors=["Please upload the datasets first."]
        )

    analysis = None
    search_error = None

    if request.method == "POST":

        driver_id = request.form.get("driver_id")

        # Search using the dictionary index.
        driver = driver_index.get(driver_id)

        if driver is None:
            search_error = "Driver not found."
        else:
            analysis = driver_analyzer.get_driver_analysis(
                driver_id
            )

    return render_template(
        "driver.html",
        drivers=drivers,
        analysis=analysis,
        search_error=search_error
    )


@app.route("/zone", methods=["GET", "POST"])
def zone_analysis():

    if zone_analyzer is None:
        return render_template(
            "index.html",
            errors=["Please upload the datasets first."]
        )

    analysis = None
    demand_distribution = None
    search_error = None

    if request.method == "POST":

        zone_name = request.form.get("zone_name")

        # Search using the dictionary index.
        zone = zone_index.get(zone_name)

        if zone is None:
            search_error = "Zone not found."
        else:
            analysis = zone_analyzer.get_zone_analysis(
                zone_name
            )

            demand_distribution = (
                zone_analyzer.get_demand_distribution(
                    zone_name
                )
            )

    return render_template(
        "zone.html",
        zones=zones,
        analysis=analysis,
        demand_distribution=demand_distribution,
        search_error=search_error
    )


@app.route("/search", methods=["POST"])
def search():

    if driver_analyzer is None:
        return render_template(
            "index.html",
            errors=["Please upload the datasets first."]
        )

    search_type = request.form.get("search_type")
    search_id = request.form.get("search_id")

    result = None
    search_error = None

    if search_type == "driver":

        result = driver_index.get(search_id)

    elif search_type == "trip":

        result = trip_index.get(search_id)

    elif search_type == "zone":

        result = zone_index.get(search_id)

    if result is None:
        search_error = "No matching result found."

    return render_template(
        "dashboard.html",
        summary={
            "drivers": len(drivers),
            "trips": len(trips),
            "activities": len(activities),
            "zones": len(zones)
        },
        trip_summary={
            "total_trips": trip_analyzer.get_total_trips(),
            "completed_trips": trip_analyzer.get_completed_trips(),
            "cancelled_trips": trip_analyzer.get_cancelled_trips(),
            "total_revenue": trip_analyzer.get_total_revenue(),
            "average_fare": trip_analyzer.get_average_fare(),
            "average_distance": trip_analyzer.get_average_distance(),
            "average_duration": trip_analyzer.get_average_duration()
        },
        errors=[],
        search_result=result,
        search_error=search_error
    )

@app.route("/driver-rankings", methods=["POST"])
def driver_rankings():

    if driver_analyzer is None:
        return render_template(
            "index.html",
            errors=["Please upload the datasets first."]
        )

    metric = request.form.get("metric")

    if metric == "completed_trips":

        rankings = (
            driver_analyzer.get_drivers_by_completed_trips()
        )

    elif metric == "revenue":

        rankings = (
            driver_analyzer.get_drivers_by_revenue()
        )

    elif metric == "cancellation_rate":

        rankings = (
            driver_analyzer.get_drivers_by_cancellation_rate()
        )

    else:
        rankings = []

    return render_template(
        "dashboard.html",
        summary={
            "drivers": len(drivers),
            "trips": len(trips),
            "activities": len(activities),
            "zones": len(zones)
        },
        trip_summary={
            "total_trips": trip_analyzer.get_total_trips(),
            "completed_trips": trip_analyzer.get_completed_trips(),
            "cancelled_trips": trip_analyzer.get_cancelled_trips(),
            "total_revenue": trip_analyzer.get_total_revenue(),
            "average_fare": trip_analyzer.get_average_fare(),
            "average_distance": trip_analyzer.get_average_distance(),
            "average_duration": trip_analyzer.get_average_duration()
        },
        errors=[],
        rankings=rankings,
        ranking_metric=metric
    )

if __name__ == "__main__":
    app.run(debug=True)