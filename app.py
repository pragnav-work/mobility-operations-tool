import os

from flask import Flask, render_template, request

from services.data_loader import DataLoader
from services.validation_service import DataValidator


app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

loader = DataLoader()
validator = DataValidator()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():

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

    # First check that all required columns exist.
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

    # Stop if the file structure itself is incorrect.
    if structure_errors:
        return render_template(
            "index.html",
            errors=structure_errors
        )

    # Validate the actual data.
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

    # Create Python objects from the uploaded data.
    drivers = loader.load_drivers(drivers_path)
    trips = loader.load_trips(trips_path)
    activities = loader.load_activities(activities_path)

    # Validate relationships between datasets.
    validation_errors.extend(
        validator.validate_driver_ids(
            trips,
            drivers
        )
    )

    # Create zone objects.
    zones = loader.load_zones(trips)

    # Prepare Day 1 summary.
    summary = {
        "drivers": len(drivers),
        "trips": len(trips),
        "activities": len(activities),
        "zones": len(zones)
    }

    return render_template(
        "dashboard.html",
        summary=summary,
        errors=validation_errors
    )


if __name__ == "__main__":
    app.run(debug=True)