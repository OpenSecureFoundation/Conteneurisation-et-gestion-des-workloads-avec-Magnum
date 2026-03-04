"""
routes/clusters.py  –  Routes API pour la gestion des clusters Magnum
"""
from flask import Blueprint, jsonify, request
from services import magnum_service

bp = Blueprint("clusters", __name__, url_prefix="/api/clusters")


@bp.route("/", methods=["GET"])
def list_clusters():
    try:
        return jsonify({"clusters": magnum_service.list_clusters()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cluster_id>", methods=["GET"])
def get_cluster(cluster_id):
    try:
        return jsonify(magnum_service.get_cluster(cluster_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/", methods=["POST"])
def create_cluster():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("cluster_template_id"):
        return jsonify({"error": "name et cluster_template_id sont requis"}), 400
    try:
        return jsonify(magnum_service.create_cluster(data)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cluster_id>", methods=["DELETE"])
def delete_cluster(cluster_id):
    try:
        return jsonify(magnum_service.delete_cluster(cluster_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cluster_id>/scale", methods=["POST"])
def scale_cluster(cluster_id):
    data = request.get_json()
    node_count = data.get("node_count") if data else None
    if node_count is None:
        return jsonify({"error": "node_count est requis"}), 400
    try:
        return jsonify(magnum_service.scale_cluster(cluster_id, node_count))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<cluster_id>/config", methods=["GET"])
def get_cluster_config(cluster_id):
    try:
        return jsonify(magnum_service.get_cluster_config(cluster_id))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
