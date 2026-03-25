from services.openstack_client import get_connection

def list_cluster_templates():
    conn = get_connection()
    return [_fmt_tpl(t) for t in conn.container_infrastructure_management.cluster_templates()]

def get_cluster_template(tid):
    conn = get_connection()
    return _fmt_tpl(conn.container_infrastructure_management.get_cluster_template(tid))

def create_cluster_template(data):
    conn = get_connection()
    t = conn.container_infrastructure_management.create_cluster_template(
        name=data["name"], image_id=data["image_id"], coe=data["coe"],
        keypair_id=data.get("keypair_id", ""), flavor_id=data.get("flavor_id", "m1.small"),
        master_flavor_id=data.get("master_flavor_id", "m1.medium"),
        docker_volume_size=int(data.get("docker_volume_size", 50)),
        network_driver=data.get("network_driver", "flannel"),
        external_network_id=data.get("external_network_id", "public"),
        dns_nameserver=data.get("dns_nameserver", "8.8.8.8"),
        master_lb_enabled=data.get("master_lb_enabled", True),
        floating_ip_enabled=data.get("floating_ip_enabled", True),
        public=data.get("public", False),
    )
    return _fmt_tpl(t)

def delete_cluster_template(tid):
    conn = get_connection()
    conn.container_infrastructure_management.delete_cluster_template(tid)
    return {"status": "deleted", "id": tid}

def _fmt_tpl(t):
    return {"id": t.id, "name": t.name, "coe": t.coe, "image_id": t.image_id,
            "flavor_id": t.flavor_id, "master_flavor_id": t.master_flavor_id,
            "network_driver": t.network_driver, "docker_volume_size": t.docker_volume_size,
            "public": t.is_public, "created_at": str(t.created_at) if t.created_at else None}

def list_clusters():
    conn = get_connection()
    return [_fmt_cluster(c) for c in conn.container_infrastructure_management.clusters()]

def get_cluster(cid):
    conn = get_connection()
    return _fmt_cluster(conn.container_infrastructure_management.get_cluster(cid))

def create_cluster(data):
    conn = get_connection()
    c = conn.container_infrastructure_management.create_cluster(
        name=data["name"], cluster_template_id=data["cluster_template_id"],
        master_count=int(data.get("master_count", 1)),
        node_count=int(data.get("node_count", 1)),
        keypair=data.get("keypair", ""),
        create_timeout=int(data.get("create_timeout", 60)),
    )
    return _fmt_cluster(c)

def delete_cluster(cid):
    conn = get_connection()
    conn.container_infrastructure_management.delete_cluster(cid)
    return {"status": "deleted", "id": cid}

def scale_cluster(cid, node_count):
    conn = get_connection()
    conn.container_infrastructure_management.update_cluster(
        cid, [{"op": "replace", "path": "/node_count", "value": int(node_count)}])
    return {"status": "scaling", "cluster_id": cid, "node_count": node_count}

def get_cluster_config(cid):
    conn = get_connection()
    try:
        cfg = conn.container_infrastructure_management.get_cluster_kubeconfig(cid)
        return {"kubeconfig": cfg}
    except Exception as e:
        return {"error": str(e)}

def _fmt_cluster(c):
    return {"id": c.id, "name": c.name, "status": c.status,
            "status_reason": getattr(c, "status_reason", None),
            "cluster_template_id": c.cluster_template_id,
            "master_count": c.master_count, "node_count": c.node_count,
            "keypair": getattr(c, "keypair", None),
            "master_addresses": getattr(c, "master_addresses", []),
            "node_addresses": getattr(c, "node_addresses", []),
            "coe_version": getattr(c, "coe_version", None),
            "created_at": str(c.created_at) if c.created_at else None,
            "updated_at": str(c.updated_at) if c.updated_at else None}
