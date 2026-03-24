"""
routes/templates.py  –  Routes API pour les cluster templates Magnum
"""
from flask import Blueprint, jsonify, request
from services import magnum_service

bp = Blueprint("templates", __name__, url_prefix="/api/templates")


@bp.route("/", methods=["GET"])
def list_templates():
    try:
        return jsonify({"templates": magnum_service.list_cluster_templates()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<template_id>", methods=["GET"])
def get_template(template_id):
    try:
        return jsonify(magnum_service.get_cluster_template(template_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/", methods=["POST"])
def create_template():
    data = request.get_json()
    required = ["name", "image_id", "coe"]
    for field in required:
        if not data or not data.get(field):
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400
    try:
        return jsonify(magnum_service.create_cluster_template(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<template_id>", methods=["DELETE"])
def delete_template(template_id):
    try:
        return jsonify(magnum_service.delete_cluster_template(template_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
