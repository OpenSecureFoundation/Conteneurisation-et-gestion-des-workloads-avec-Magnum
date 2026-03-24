"""
services/magnum_service.py
Service layer pour toutes les opérations Magnum (clusters, templates, scaling)
"""
from services.openstack_client import get_connection
import openstack.exceptions


# ─────────────────────────────────────────────
# CLUSTER TEMPLATES
# ─────────────────────────────────────────────

def list_cluster_templates():
    conn = get_connection()
    templates = list(conn.container_infrastructure_management.cluster_templates())
    return [_fmt_template(t) for t in templates]


def get_cluster_template(template_id):
    conn = get_connection()
    t = conn.container_infrastructure_management.get_cluster_template(template_id)
    return _fmt_template(t)


def create_cluster_template(data):
    conn = get_connection()
    payload = {
        "name": data["name"],
        "image_id": data["image_id"],
        "keypair_id": data.get("keypair_id", ""),
        "coe": data["coe"],  # kubernetes | swarm | swarm-mode
        "flavor_id": data.get("flavor_id", "m1.small"),
        "master_flavor_id": data.get("master_flavor_id", "m1.medium"),
        "docker_volume_size": int(data.get("docker_volume_size", 50)),
        "network_driver": data.get("network_driver", "flannel"),
        "external_network_id": data.get("external_network_id", "public"),
        "dns_nameserver": data.get("dns_nameserver", "8.8.8.8"),
        "master_lb_enabled": data.get("master_lb_enabled", True),
        "floating_ip_enabled": data.get("floating_ip_enabled", True),
        "volume_driver": data.get("volume_driver", "cinder"),
        "public": data.get("public", False),
        "hidden": data.get("hidden", False),
    }
    t = conn.container_infrastructure_management.create_cluster_template(**payload)
    return _fmt_template(t)


def delete_cluster_template(template_id):
    conn = get_connection()
    conn.container_infrastructure_management.delete_cluster_template(template_id)
    return {"status": "deleted", "id": template_id}


def _fmt_template(t):
    return {
        "id": t.id,
        "name": t.name,
        "coe": t.coe,
        "image_id": t.image_id,
        "flavor_id": t.flavor_id,
        "master_flavor_id": t.master_flavor_id,
        "network_driver": t.network_driver,
        "docker_volume_size": t.docker_volume_size,
        "public": t.is_public,
        "hidden": t.is_hidden,
        "created_at": str(t.created_at) if t.created_at else None,
    }


# ─────────────────────────────────────────────
# CLUSTERS
# ─────────────────────────────────────────────

def list_clusters():
    conn = get_connection()
    clusters = list(conn.container_infrastructure_management.clusters())
    return [_fmt_cluster(c) for c in clusters]


def get_cluster(cluster_id):
    conn = get_connection()
    c = conn.container_infrastructure_management.get_cluster(cluster_id)
    return _fmt_cluster(c)


def create_cluster(data):
    conn = get_connection()
    payload = {
        "name": data["name"],
        "cluster_template_id": data["cluster_template_id"],
        "master_count": int(data.get("master_count", 1)),
        "node_count": int(data.get("node_count", 1)),
        "keypair": data.get("keypair", ""),
        "create_timeout": int(data.get("create_timeout", 60)),
    }
    c = conn.container_infrastructure_management.create_cluster(**payload)
    return _fmt_cluster(c)


def delete_cluster(cluster_id):
    conn = get_connection()
    conn.container_infrastructure_management.delete_cluster(cluster_id)
    return {"status": "deleted", "id": cluster_id}


def scale_cluster(cluster_id, node_count):
    """Met à l'échelle le nombre de worker nodes d'un cluster."""
    conn = get_connection()
    conn.container_infrastructure_management.update_cluster(
        cluster_id,
        [{"op": "replace", "path": "/node_count", "value": int(node_count)}]
    )
    return {"status": "scaling", "cluster_id": cluster_id, "node_count": node_count}


def get_cluster_config(cluster_id):
    """Récupère le kubeconfig du cluster."""
    conn = get_connection()
    try:
        cfg = conn.container_infrastructure_management.get_cluster_kubeconfig(cluster_id)
        return {"kubeconfig": cfg}
    except Exception as e:
        return {"error": str(e)}


def _fmt_cluster(c):
    return {
        "id": c.id,
        "name": c.name,
        "status": c.status,
        "status_reason": getattr(c, "status_reason", None),
        "cluster_template_id": c.cluster_template_id,
        "master_count": c.master_count,
        "node_count": c.node_count,
        "keypair": getattr(c, "keypair", None),
        "master_addresses": getattr(c, "master_addresses", []),
        "node_addresses": getattr(c, "node_addresses", []),
        "coe_version": getattr(c, "coe_version", None),
        "create_timeout": getattr(c, "create_timeout", None),
        "created_at": str(c.created_at) if c.created_at else None,
        "updated_at": str(c.updated_at) if c.updated_at else None,
    }
