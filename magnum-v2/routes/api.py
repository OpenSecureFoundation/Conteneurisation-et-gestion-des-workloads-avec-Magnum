from flask import Blueprint, jsonify, request
from services import heat_service, monitoring_service

# ── Stacks ─────────────────────────────────────────────────────
sb = Blueprint("stacks", __name__, url_prefix="/api/stacks")

@sb.route("/", methods=["GET"])
def list_stacks():
    try: return jsonify({"stacks": heat_service.list_stacks()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/<sid>", methods=["GET"])
def get_stack(sid):
    try:
        s = heat_service.get_stack(sid)
        return jsonify(s) if s else (jsonify({"error": "Not found"}), 404)
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/hybrid", methods=["POST"])
def create_hybrid():
    data = request.get_json()
    for f in ["stack_name", "cluster_template_id", "keypair"]:
        if not data or not data.get(f): return jsonify({"error": f"'{f}' requis"}), 400
    try: return jsonify(heat_service.create_hybrid_stack(data)), 201
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/custom", methods=["POST"])
def create_custom():
    data = request.get_json()
    if not data or not data.get("stack_name") or not data.get("template"):
        return jsonify({"error": "stack_name et template requis"}), 400
    try: return jsonify(heat_service.create_custom_stack(data)), 201
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/<sid>", methods=["DELETE"])
def delete_stack(sid):
    try: return jsonify(heat_service.delete_stack(sid))
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/<sid>/resources", methods=["GET"])
def stack_resources(sid):
    try: return jsonify({"resources": heat_service.get_stack_resources(sid)})
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/<sid>/events", methods=["GET"])
def stack_events(sid):
    try: return jsonify({"events": heat_service.get_stack_events(sid)})
    except Exception as e: return jsonify({"error": str(e)}), 500

@sb.route("/template/hybrid", methods=["GET"])
def hybrid_template():
    return jsonify({"template": heat_service.get_hybrid_template()})


# ── Monitoring ─────────────────────────────────────────────────
mb = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")

@mb.route("/summary", methods=["GET"])
def summary():
    try: return jsonify(monitoring_service.get_dashboard_summary())
    except Exception as e: return jsonify({"error": str(e)}), 500

@mb.route("/compute", methods=["GET"])
def compute():
    try: return jsonify(monitoring_service.get_compute_metrics())
    except Exception as e: return jsonify({"error": str(e)}), 500

@mb.route("/alarms", methods=["GET"])
def list_alarms():
    return jsonify({"alarms": monitoring_service.get_alarms()})

@mb.route("/alarms", methods=["POST"])
def create_alarm():
    data = request.get_json()
    if not data or not data.get("name"): return jsonify({"error": "name requis"}), 400
    try: return jsonify(monitoring_service.create_alarm(data)), 201
    except Exception as e: return jsonify({"error": str(e)}), 500

@mb.route("/alarms/<aid>", methods=["DELETE"])
def delete_alarm(aid):
    try: return jsonify(monitoring_service.delete_alarm(aid))
    except Exception as e: return jsonify({"error": str(e)}), 500

@mb.route("/servers", methods=["GET"])
def servers():
    return jsonify({"servers": monitoring_service.get_servers_list()})

@mb.route("/resources/keypairs", methods=["GET"])
def keypairs():
    return jsonify({"keypairs": monitoring_service.get_keypairs()})

@mb.route("/resources/flavors", methods=["GET"])
def flavors():
    return jsonify({"flavors": monitoring_service.get_flavors()})

@mb.route("/resources/networks", methods=["GET"])
def networks():
    return jsonify({"networks": monitoring_service.get_networks()})

@mb.route("/resources/images", methods=["GET"])
def images():
    return jsonify({"images": monitoring_service.get_images()})
