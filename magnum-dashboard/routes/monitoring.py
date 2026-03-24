"""
routes/monitoring.py  –  Routes API pour le monitoring (Gnocchi, Aodh, Nova)
"""
from flask import Blueprint, jsonify, request
from services import monitoring_service

bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")


@bp.route("/summary", methods=["GET"])
def dashboard_summary():
    try:
        return jsonify(monitoring_service.get_dashboard_summary())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/compute", methods=["GET"])
def compute_metrics():
    try:
        return jsonify(monitoring_service.get_compute_metrics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/alarms", methods=["GET"])
def list_alarms():
    try:
        return jsonify({"alarms": monitoring_service.get_alarms()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/alarms", methods=["POST"])
def create_alarm():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name est requis"}), 400
    try:
        return jsonify(monitoring_service.create_alarm(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/alarms/<alarm_id>", methods=["DELETE"])
def delete_alarm(alarm_id):
    try:
        return jsonify(monitoring_service.delete_alarm(alarm_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/servers", methods=["GET"])
def list_servers():
    try:
        return jsonify({"servers": monitoring_service.get_servers_list()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/resources/keypairs", methods=["GET"])
def list_keypairs():
    return jsonify({"keypairs": monitoring_service.get_keypairs()})


@bp.route("/resources/flavors", methods=["GET"])
def list_flavors():
    return jsonify({"flavors": monitoring_service.get_flavors()})


@bp.route("/resources/networks", methods=["GET"])
def list_networks():
    return jsonify({"networks": monitoring_service.get_networks()})


@bp.route("/resources/images", methods=["GET"])
def list_images():
    return jsonify({"images": monitoring_service.get_images()})
