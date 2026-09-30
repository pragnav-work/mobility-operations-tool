import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

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


@app.template_filter("number")
def format_number(value):
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return value


@app.template_filter("integer")
def format_integer(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value


def reset_application_data():
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


def data_is_loaded():
    return (
        driver_analyzer is not None
        and trip_analyzer is not None
        and zone_analyzer is not None
        and utilization_analyzer is not None
    )


def group_validation_errors(errors):
    groups = {
        "Missing Values": [],
        "Duplicate Records": [],
        "Invalid IDs": [],
        "Invalid Timestamps": [],
        "Negative Values": [],
        "Invalid Trip Duration": [],
        "Missing Columns / File Structure": [],
        "Other Validation Issues": []
    }

    for error in errors:

        text = str(error).lower()

        if "duplicate" in text:
            category = "Duplicate Records"

        elif (
            "missing column" in text
            or "required column" in text
            or "empty file" in text
            or "read error" in text
        ):
            category = "Missing Columns / File Structure"

        elif (
            "unknown driver" in text
            or "invalid id" in text
            or "driver id" in text and "invalid" in text
        ):
            category = "Invalid IDs"

        elif (
            "timestamp" in text
            or "date" in text and "invalid" in text
        ):
            category = "Invalid Timestamps"

        elif (
            "negative fare" in text
            or "negative distance" in text
            or "negative value" in text
        ):
            category = "Negative Values"

        elif (
            "duration" in text
            or "drop time" in text
            or "pickup time" in text and "drop" in text
        ):
            category = "Invalid Trip Duration"

        elif "missing" in text:
            category = "Missing Values"

        else:
            category = "Other Validation Issues"

        groups[category].append(error)

    return {
        key: value
        for key, value in groups.items()
        if value
    }


def load_uploaded_data():

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

    # Structural problems prevent object creation.
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

    # Row-level validation errors are displayed, but valid objects
    # are still created so the evaluator can inspect the analytics.
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

    # Important:
    # Do not reload old files from data/uploads/.
    # Data becomes available only after the current application
    # receives an upload.
    return data_is_loaded()


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

    active_drivers = 0

    for driver in drivers:
        if driver.is_active():
            active_drivers += 1

    rider_ids = set()

    for trip in trips:
        if trip.rider_id:
            rider_ids.add(trip.rider_id)

    total_trips = (
        trip_analyzer.get_total_trips()
        if trip_analyzer
        else 0
    )

    completed_trips = (
        trip_analyzer.get_completed_trips()
        if trip_analyzer
        else 0
    )

    cancelled_trips = (
        trip_analyzer.get_cancelled_trips()
        if trip_analyzer
        else 0
    )

    completion_rate = 0
    cancellation_rate = 0

    if total_trips > 0:
        completion_rate = (
            completed_trips / total_trips
        ) * 100

        cancellation_rate = (
            cancelled_trips / total_trips
        ) * 100

    return {
        "summary": {
            "drivers": len(drivers),
            "active_drivers": active_drivers,
            "riders": len(rider_ids),
            "trips": len(trips),
            "activities": len(activities),
            "zones": len(zones)
        },

        "trip_summary": {
            "total_trips": total_trips,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "completion_rate": completion_rate,
            "cancellation_rate": cancellation_rate,
            "total_revenue": (
                trip_analyzer.get_total_revenue()
                if trip_analyzer
                else 0
            ),
            "average_fare": (
                trip_analyzer.get_average_fare()
                if trip_analyzer
                else 0
            ),
            "average_distance": (
                trip_analyzer.get_average_distance()
                if trip_analyzer
                else 0
            ),
            "average_duration": (
                trip_analyzer.get_average_duration()
                if trip_analyzer
                else 0
            )
        },

        "peak_demand": peak_demand,
        "cancellation_intelligence": cancellation_intelligence,
        "utilization_results": utilization_results,
        "anomalies": anomalies,
        "insights": insights
    }


@app.route("/")
def index():

    return render_template(
        "index.html",
        data_loaded=data_is_loaded()
    )


@app.route("/validation")
def validation():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before opening validation."
            ]
        )

    return render_template(
        "validation.html",
        errors=validation_errors,
        grouped_errors=group_validation_errors(
            validation_errors
        ),
        data_loaded=True
    )


@app.route("/analysis")
def analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before opening analysis."
            ]
        )

    context = get_dashboard_context()

    context["errors"] = validation_errors

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/dashboard")
def dashboard():

    return analysis()


@app.route("/upload", methods=["POST"])
def upload_files():

    reset_application_data()

    drivers_file = request.files.get("drivers")
    trips_file = request.files.get("trips")
    activities_file = request.files.get("activities")

    if (
        not drivers_file
        or not trips_file
        or not activities_file
    ):

        return render_template(
            "index.html",
            data_loaded=False,
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

    if not load_uploaded_data():

        return render_template(
            "validation.html",
            errors=validation_errors,
            grouped_errors=group_validation_errors(
                validation_errors
            ),
            data_loaded=False
        )

    return render_template(
        "validation.html",
        errors=validation_errors,
        grouped_errors=group_validation_errors(
            validation_errors
        ),
        data_loaded=True
    )


@app.route("/driver", methods=["GET", "POST"])
def driver_analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before opening driver analytics."
            ]
        )

    analysis_result = None
    search_error = None

    if request.method == "POST":

        driver_id = request.form.get("driver_id")

        driver = driver_index.get(
            normalize_key(driver_id)
        )

        if driver is None:

            search_error = "Driver not found."

        else:

            analysis_result = (
                driver_analyzer.get_driver_analysis(
                    driver.driver_id
                )
            )

    return render_template(
        "driver.html",
        drivers=drivers,
        analysis=analysis_result,
        search_error=search_error
    )


@app.route("/zone", methods=["GET", "POST"])
def zone_analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before opening zone analytics."
            ]
        )

    analysis_result = None
    demand_distribution = None
    search_error = None

    if request.method == "POST":

        zone_name = request.form.get("zone_name")

        zone = zone_index.get(
            normalize_key(zone_name)
        )

        if zone is None:

            search_error = "Zone not found."

        else:

            analysis_result = (
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
        analysis=analysis_result,
        demand_distribution=demand_distribution,
        search_error=search_error
    )


@app.route("/search", methods=["POST"])
def search():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before searching."
            ]
        )

    search_type = request.form.get("search_type")
    search_id = request.form.get("search_id")

    result = None
    search_error = None

    search_key = normalize_key(search_id)

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

        search_error = "No matching result found."

    context = get_dashboard_context()

    context["search_result"] = result
    context["search_error"] = search_error
    context["open_section"] = "search"

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/driver-rankings", methods=["POST"])
def driver_rankings():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before ranking drivers."
            ]
        )

    metric = request.form.get("metric")

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

    context["rankings"] = rankings
    context["ranking_metric"] = metric
    context["open_section"] = "rankings"

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/top-k", methods=["POST"])
def top_k():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before running Top-K analysis."
            ]
        )

    metric = request.form.get("metric")
    k = request.form.get("k")

    try:

        k = int(k)

        if k < 1:
            k = 5

    except (ValueError, TypeError):

        k = 5

    results = []

    if metric == "completed_trips":

        results = driver_analyzer.get_top_k_drivers(
            "completed_trips",
            k
        )

    elif metric == "revenue":

        results = driver_analyzer.get_top_k_drivers(
            "revenue",
            k
        )

    elif metric == "zone_demand":

        results = zone_analyzer.get_top_k_zones(
            "demand",
            k
        )

    elif metric == "zone_cancellation":

        results = zone_analyzer.get_top_k_zones(
            "cancellation",
            k
        )

    elif metric == "rider_trips":

        results = trip_analyzer.get_top_k_riders(
            k
        )

    context = get_dashboard_context()

    context["top_k_results"] = results
    context["top_k_metric"] = metric
    context["open_section"] = "top_k"

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/idle-time", methods=["POST"])
def idle_time_analysis():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before running idle-time analysis."
            ]
        )

    threshold = request.form.get("threshold")

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

    context["idle_periods"] = idle_periods
    context["idle_threshold"] = threshold
    context["open_section"] = "idle"

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/utilization", methods=["POST"])
def utilization():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before running utilization analysis."
            ]
        )

    high_threshold = request.form.get("high_threshold")
    medium_threshold = request.form.get("medium_threshold")

    try:
        high_threshold = float(high_threshold)
    except (ValueError, TypeError):
        high_threshold = 70

    try:
        medium_threshold = float(medium_threshold)
    except (ValueError, TypeError):
        medium_threshold = 40

    utilization_results = (
        utilization_analyzer.get_driver_utilization(
            high_threshold,
            medium_threshold
        )
    )

    context = get_dashboard_context()

    context["utilization_results"] = utilization_results
    context["high_threshold"] = high_threshold
    context["medium_threshold"] = medium_threshold
    context["open_section"] = "utilization"

    return render_template(
        "dashboard.html",
        **context
    )


@app.route("/anomalies", methods=["GET", "POST"])
def anomalies():

    if not ensure_data_loaded():

        return render_template(
            "index.html",
            data_loaded=False,
            errors=[
                "Upload the three datasets before opening anomaly detection."
            ]
        )

    utilization_results = (
        utilization_analyzer.get_driver_utilization(
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
                request.form.get("long_duration")
            )

            thresholds["fare_multiplier"] = float(
                request.form.get("fare_multiplier")
            )

            thresholds["cancellation"] = float(
                request.form.get("cancellation")
            )

            thresholds["utilization"] = float(
                request.form.get("utilization")
            )

            thresholds["trip_count"] = int(
                request.form.get("trip_count")
            )

            thresholds["rating"] = float(
                request.form.get("rating")
            )

        except (ValueError, TypeError):

            pass

    anomaly_results = detector.get_all_anomalies(
        thresholds["long_duration"],
        thresholds["fare_multiplier"],
        thresholds["cancellation"],
        thresholds["utilization"],
        thresholds["trip_count"],
        thresholds["rating"]
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
        data_loaded=data_is_loaded(),
        errors=[
            "The requested page was not found."
        ]
    ), 404


@app.errorhandler(500)
def internal_error(error):

    return render_template(
        "index.html",
        data_loaded=data_is_loaded(),
        errors=[
            "An unexpected application error occurred."
        ]
    ), 500


if __name__ == "__main__":
    app.run(debug=True)