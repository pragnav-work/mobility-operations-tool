import os

from flask import Flask, render_template, request

from services.data_loader import DataLoader
from services.validation_service import DataValidator
from services.driver_analyzer import DriverAnalyzer
from services.trip_analyzer import TripAnalyzer
from services.zone_analyzer import ZoneAnalyzer
from services.utilization_analyzer import UtilizationAnalyzer
from services.anomaly_detector import AnomalyDetector
from services.insights_engine import InsightsEngine


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
utilization_analyzer = None

driver_index = {}
trip_index = {}
zone_index = {}

validation_errors = []


def normalize_key(value):
    if value is None:
        return ""

    return str(value).strip().casefold()


def load_saved_data():

    global drivers
    global trips
    global activities
    global zones

    global driver_analyzer
    global trip_analyzer
    global zone_analyzer
    global utilization_analyzer

    global driver_index
    global trip_index
    global zone_index

    global validation_errors

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

    if not (
        os.path.exists(drivers_path)
        and os.path.exists(trips_path)
        and os.path.exists(activities_path)
    ):
        return False

    validation_errors = []

    validation_errors.extend(
        validator.validate_file_structure(
            drivers_path,
            "drivers"
        )
    )

    validation_errors.extend(
        validator.validate_file_structure(
            trips_path,
            "trips"
        )
    )

    validation_errors.extend(
        validator.validate_file_structure(
            activities_path,
            "activities"
        )
    )

    if validation_errors:
        return False

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

    drivers = loader.load_drivers(
        drivers_path
    )

    trips = loader.load_trips(
        trips_path
    )

    activities = loader.load_activities(
        activities_path
    )

    validation_errors.extend(
        validator.validate_driver_ids(
            trips,
            drivers
        )
    )

    zones = loader.load_zones(
        trips
    )

    driver_analyzer = DriverAnalyzer(
        drivers,
        trips
    )

    trip_analyzer = TripAnalyzer(
        trips
    )

    zone_analyzer = ZoneAnalyzer(
        trips
    )

    utilization_analyzer = UtilizationAnalyzer(
        activities
    )

    driver_index = {}

    for driver in drivers:
        driver_index[
            normalize_key(driver.driver_id)
        ] = driver

    trip_index = {}

    for trip in trips:
        trip_index[
            normalize_key(trip.trip_id)
        ] = trip

    zone_index = {}

    for zone in zones:
        zone_index[
            normalize_key(zone.zone_name)
        ] = zone

    return True


def ensure_data_loaded():

    if driver_analyzer is not None:
        return True

    return load_saved_data()


def get_dashboard_context():

    utilization_results = []

    if utilization_analyzer is not None:

        utilization_results = (
            utilization_analyzer.get_driver_utilization(
                70,
                40
            )
        )

    anomalies = []

    if (
        driver_analyzer is not None
        and trip_analyzer is not None
    ):

        anomaly_detector = AnomalyDetector(
            drivers,
            trips,
            utilization_results
        )

        anomalies = (
            anomaly_detector.get_all_anomalies()
        )

    cancellation_intelligence = []

    if trip_analyzer is not None:

        cancellation_intelligence = (
            trip_analyzer.get_cancellation_intelligence()
        )

    insights = []

    if (
        zone_analyzer is not None
        and trip_analyzer is not None
    ):

        insights_engine = InsightsEngine(
            zone_analyzer,
            trip_analyzer,
            cancellation_intelligence,
            utilization_results,
            anomalies
        )

        insights = (
            insights_engine.generate_insights()
        )

    peak_demand = None

    if trip_analyzer is not None:

        peak_demand = (
            trip_analyzer.get_peak_demand()
        )

    return {
        "summary": {
            "drivers": len(drivers),
            "trips": len(trips),
            "activities": len(activities),
            "zones": len(zones)
        },

        "trip_summary": {
            "total_trips": (
                trip_analyzer.get_total_trips()
                if trip_analyzer else 0
            ),

            "completed_trips": (
                trip_analyzer.get_completed_trips()
                if trip_analyzer else 0
            ),

            "cancelled_trips": (
                trip_analyzer.get_cancelled_trips()
                if trip_analyzer else 0
            ),

            "total_revenue": (
                trip_analyzer.get_total_revenue()
                if trip_analyzer else 0
            ),

            "average_fare": (
                trip_analyzer.get_average_fare()
                if trip_analyzer else 0
            ),

            "average_distance": (
                trip_analyzer.get_average_distance()
                if trip_analyzer else 0
            ),

            "average_duration": (
                trip_analyzer.get_average_duration()
                if trip_analyzer else 0
            )
        },

        "peak_demand": peak_demand,

        "cancellation_intelligence":
            cancellation_intelligence,

        "utilization_results":
            utilization_results,

        "anomalies":
            anomalies,

        "insights":
            insights
    }


@app.route("/")
def index():
    return render_template(
        "index.html"
    )


@app.route("/dashboard")
def dashboard():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    context = get_dashboard_context()

    context["errors"] = validation_errors

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/upload", methods=["POST"])
def upload_files():

    global validation_errors

    drivers_file = request.files.get(
        "drivers"
    )

    trips_file = request.files.get(
        "trips"
    )

    activities_file = request.files.get(
        "activities"
    )

    if (
        not drivers_file
        or not trips_file
        or not activities_file
    ):

        return render_template(
            "index.html",
            errors=[
                "Please upload all three CSV files."
            ]
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

    drivers_file.save(
        drivers_path
    )

    trips_file.save(
        trips_path
    )

    activities_file.save(
        activities_path
    )

    if not load_saved_data():

        return render_template(
            "index.html",
            errors=validation_errors
        )

    context = get_dashboard_context()

    context["errors"] = validation_errors

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/driver", methods=["GET", "POST"])
def driver_analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    analysis = None
    search_error = None

    if request.method == "POST":

        driver_id = request.form.get(
            "driver_id"
        )

        driver = driver_index.get(
            normalize_key(driver_id)
        )

        if driver is None:

            search_error = "Driver not found."

        else:

            analysis = (
                driver_analyzer.get_driver_analysis(
                    driver.driver_id
                )
            )

    return render_template(
        "driver.html",
        drivers=drivers,
        analysis=analysis,
        search_error=search_error
    )


@app.route("/zone", methods=["GET", "POST"])
def zone_analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    analysis = None
    demand_distribution = None
    search_error = None

    if request.method == "POST":

        zone_name = request.form.get(
            "zone_name"
        )

        zone = zone_index.get(
            normalize_key(zone_name)
        )

        if zone is None:

            search_error = "Zone not found."

        else:

            analysis = (
                zone_analyzer.get_zone_analysis(
                    zone.zone_name
                )
            )

            demand_distribution = (
                zone_analyzer.get_demand_distribution(
                    zone.zone_name
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

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    search_type = request.form.get(
        "search_type"
    )

    search_id = request.form.get(
        "search_id"
    )

    result = None
    search_error = None

    search_key = normalize_key(
        search_id
    )

    if search_type == "driver":

        result = driver_index.get(
            search_key
        )

    elif search_type == "trip":

        result = trip_index.get(
            search_key
        )

    elif search_type == "zone":

        result = zone_index.get(
            search_key
        )

    if result is None:

        search_error = (
            "No matching result found."
        )

    context = get_dashboard_context()

    context["errors"] = []
    context["search_result"] = result
    context["search_error"] = search_error

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/driver-rankings", methods=["POST"])
def driver_rankings():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    metric = request.form.get(
        "metric"
    )

    if metric == "completed_trips":

        rankings = (
            driver_analyzer
            .get_drivers_by_completed_trips()
        )

    elif metric == "revenue":

        rankings = (
            driver_analyzer
            .get_drivers_by_revenue()
        )

    elif metric == "cancellation_rate":

        rankings = (
            driver_analyzer
            .get_drivers_by_cancellation_rate()
        )

    else:

        rankings = []

    context = get_dashboard_context()

    context["errors"] = []
    context["rankings"] = rankings
    context["ranking_metric"] = metric

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/top-k", methods=["POST"])
def top_k():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    metric = request.form.get(
        "metric"
    )

    k = request.form.get(
        "k"
    )

    try:

        k = int(k)

        if k < 1:
            k = 5

    except (ValueError, TypeError):

        k = 5

    results = []

    if metric == "completed_trips":

        results = (
            driver_analyzer.get_top_k_drivers(
                "completed_trips",
                k
            )
        )

    elif metric == "revenue":

        results = (
            driver_analyzer.get_top_k_drivers(
                "revenue",
                k
            )
        )

    elif metric == "zone_demand":

        results = (
            zone_analyzer.get_top_k_zones(
                "demand",
                k
            )
        )

    elif metric == "zone_cancellation":

        results = (
            zone_analyzer.get_top_k_zones(
                "cancellation",
                k
            )
        )

    elif metric == "rider_trips":

        results = (
            trip_analyzer.get_top_k_riders(
                k
            )
        )

    context = get_dashboard_context()

    context["errors"] = []
    context["top_k_results"] = results
    context["top_k_metric"] = metric

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/idle-time", methods=["POST"])
def idle_time_analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    threshold = request.form.get(
        "threshold"
    )

    try:

        threshold = float(threshold)

        if threshold < 1:
            threshold = 30

    except (ValueError, TypeError):

        threshold = 30

    idle_periods = (
        trip_analyzer.get_idle_time_analysis(
            threshold
        )
    )

    context = get_dashboard_context()

    context["errors"] = []
    context["idle_periods"] = idle_periods
    context["idle_threshold"] = threshold

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/utilization", methods=["POST"])
def utilization():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    high_threshold = request.form.get(
        "high_threshold"
    )

    medium_threshold = request.form.get(
        "medium_threshold"
    )

    try:

        high_threshold = float(
            high_threshold
        )
    except (ValueError, TypeError):

        high_threshold = 70

    try:

        medium_threshold = float(
            medium_threshold
        )
    except (ValueError, TypeError):

        medium_threshold = 40

    utilization_results = (
        utilization_analyzer
        .get_driver_utilization(
            high_threshold,
            medium_threshold
        )
    )

    context = get_dashboard_context()

    context["errors"] = []

    # Replace the default dashboard utilization
    # with the requested thresholds.
    context["utilization_results"] = (
        utilization_results
    )

    context["high_threshold"] = (
        high_threshold
    )

    context["medium_threshold"] = (
        medium_threshold
    )

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/anomalies", methods=["GET", "POST"])
def anomalies():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            errors=[
                "Please upload the datasets first."
            ]
        )

    utilization_results = (
        utilization_analyzer
        .get_driver_utilization(
            70,
            40
        )
    )

    detector = AnomalyDetector(
        drivers,
        trips,
        utilization_results
    )

    thresholds = {
        "long_duration": 180,
        "fare_multiplier": 3,
        "cancellation": 30,
        "utilization": 40,
        "trip_count": 40,
        "rating": 3.5
    }

    if request.method == "POST":

        try:

            thresholds["long_duration"] = float(
                request.form.get(
                    "long_duration"
                )
            )

            thresholds["fare_multiplier"] = float(
                request.form.get(
                    "fare_multiplier"
                )
            )

            thresholds["cancellation"] = float(
                request.form.get(
                    "cancellation"
                )
            )

            thresholds["utilization"] = float(
                request.form.get(
                    "utilization"
                )
            )

            thresholds["trip_count"] = int(
                request.form.get(
                    "trip_count"
                )
            )

            thresholds["rating"] = float(
                request.form.get(
                    "rating"
                )
            )

        except (ValueError, TypeError):

            pass

    anomaly_results = (
        detector.get_all_anomalies(
            thresholds["long_duration"],
            thresholds["fare_multiplier"],
            thresholds["cancellation"],
            thresholds["utilization"],
            thresholds["trip_count"],
            thresholds["rating"]
        )
    )

    return render_template(
        "anomalies.html",
        anomalies=anomaly_results,
        thresholds=thresholds
    )


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html",
        errors=[
            "The requested page was not found."
        ]
    ), 404


@app.errorhandler(500)
def internal_error(error):

    return render_template(
        "index.html",
        errors=[
            "An unexpected application error occurred."
        ]
    ), 500


if __name__ == "__main__":
    app.run(debug=True)