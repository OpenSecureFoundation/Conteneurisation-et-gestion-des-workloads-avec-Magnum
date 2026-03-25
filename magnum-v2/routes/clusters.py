from flask import Blueprint, jsonify, request
from services import magnum_service

bp = Blueprint("clusters", __name__, url_prefix="/api/clusters")

@bp.route("/", methods=["GET"])
def list_clusters():
    try: return jsonify({"clusters": magnum_service.list_clusters()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@bp.route("/<cid>", methods=["GET"])
def get_cluster(cid):
    try: return jsonify(magnum_service.get_cluster(cid))
    except Exception as e: return jsonify({"error": str(e)}), 404

@bp.route("/", methods=["POST"])
def create_cluster():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("cluster_template_id"):
        return jsonify({"error": "name et cluster_template_id requis"}), 400
    try: return jsonify(magnum_service.create_cluster(data)), 201
    except Exception as e: return jsonify({"error": str(e)}), 500

@bp.route("/<cid>", methods=["DELETE"])
def delete_cluster(cid):
    try: return jsonify(magnum_service.delete_cluster(cid))
    except Exception as e: return jsonify({"error": str(e)}), 500

@bp.route("/<cid>/scale", methods=["POST"])
def scale_cluster(cid):
    data = request.get_json()
    n = data.get("node_count") if data else None
    if n is None: return jsonify({"error": "node_count requis"}), 400
    try: return jsonify(magnum_service.scale_cluster(cid, n))
    except Exception as e: return jsonify({"error": str(e)}), 500

@bp.route("/<cid>/config", methods=["GET"])
def get_config(cid):
    try: return jsonify(magnum_service.get_cluster_config(cid))
    except Exception as e: return jsonify({"error": str(e)}), 500
