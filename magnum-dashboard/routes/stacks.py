"""
routes/stacks.py  –  Routes API pour les stacks Heat hybrides
"""
from flask import Blueprint, jsonify, request
from services import heat_service

bp = Blueprint("stacks", __name__, url_prefix="/api/stacks")


@bp.route("/", methods=["GET"])
def list_stacks():
    try:
        return jsonify({"stacks": heat_service.list_stacks()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<stack_id>", methods=["GET"])
def get_stack(stack_id):
    try:
        s = heat_service.get_stack(stack_id)
        if not s:
            return jsonify({"error": "Stack non trouvée"}), 404
        return jsonify(s)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/hybrid", methods=["POST"])
def create_hybrid_stack():
    data = request.get_json()
    required = ["stack_name", "cluster_template_id", "keypair"]
    for field in required:
        if not data or not data.get(field):
            return jsonify({"error": f"Le champ '{field}' est requis"}), 400
    try:
        return jsonify(heat_service.create_hybrid_stack(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/custom", methods=["POST"])
def create_custom_stack():
    data = request.get_json()
    if not data or not data.get("stack_name") or not data.get("template"):
        return jsonify({"error": "stack_name et template sont requis"}), 400
    try:
        return jsonify(heat_service.create_custom_stack(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<stack_id>", methods=["DELETE"])
def delete_stack(stack_id):
    try:
        return jsonify(heat_service.delete_stack(stack_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<stack_id>/resources", methods=["GET"])
def get_stack_resources(stack_id):
    try:
        return jsonify({"resources": heat_service.get_stack_resources(stack_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<stack_id>/events", methods=["GET"])
def get_stack_events(stack_id):
    try:
        return jsonify({"events": heat_service.get_stack_events(stack_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/template/hybrid", methods=["GET"])
def get_hybrid_template():
    return jsonify({"template": heat_service.get_hybrid_template()})
