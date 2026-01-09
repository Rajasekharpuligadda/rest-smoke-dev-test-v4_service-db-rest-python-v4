from flask import Blueprint, jsonify

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    Welcome endpoint
    """
    return jsonify({"status": "ok", "message": "Welcome to the API!"}), 200
