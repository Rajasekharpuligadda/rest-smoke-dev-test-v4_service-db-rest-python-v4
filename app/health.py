from flask import Blueprint, jsonify

health = Blueprint("health", __name__, url_prefix="/service-db-rest-python-v4/health")


def check_database_connection():
    """
    Placeholder function for checking database connectivity.
    """
    # For the skeleton, we'll assume the connection is always good.
    return True, "Database connection is OK."


@health.route("/liveness")
def liveness():
    """
    Liveness Probe.
    Confirms the application process is running and can respond to requests.
    """
    return jsonify({"status": "UP", "message": "Service is alive."}), 200


@health.route("/readiness")
def readiness():
    """
    Readiness Probe.
    Confirms the application is ready to accept and process traffic.
    This is where dependency checks (e.g., database, cache) should go.
    """
    db_ok, db_msg = check_database_connection()

    if not db_ok:
        return jsonify(
            {
                "status": "DOWN",
                "dependencies": {"database": {"status": "DOWN", "message": db_msg}},
            }
        ), 503

    return jsonify(
        {
            "status": "UP",
            "dependencies": {"database": {"status": "UP", "message": db_msg}},
        }
    ), 200
