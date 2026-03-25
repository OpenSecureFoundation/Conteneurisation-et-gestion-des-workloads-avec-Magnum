from services.openstack_client import get_connection

def get_dashboard_summary():
    conn = get_connection()
    try:
        clusters = list(conn.container_infrastructure_management.clusters())
        stacks   = list(conn.orchestration.stacks())
        servers  = list(conn.compute.servers())
        networks = list(conn.network.networks())
        by_status = {}
        for c in clusters:
            s = c.status or "UNKNOWN"
            by_status[s] = by_status.get(s, 0) + 1
        return {
            "clusters": {"total": len(clusters), "by_status": by_status,
                         "running": sum(1 for c in clusters if c.status == "CREATE_COMPLETE"),
                         "creating": sum(1 for c in clusters if "IN_PROGRESS" in (c.status or "")),
                         "error": sum(1 for c in clusters if "ERROR" in (c.status or "") or "FAILED" in (c.status or ""))},
            "stacks": {"total": len(stacks),
                       "complete": sum(1 for s in stacks if "COMPLETE" in (s.status or "")),
                       "failed": sum(1 for s in stacks if "FAILED" in (s.status or ""))},
            "compute": {"servers": len(servers),
                        "active": sum(1 for s in servers if s.status == "ACTIVE")},
            "networks": len(networks),
        }
    except Exception as e:
        return {"error": str(e)}

def get_compute_metrics():
    conn = get_connection()
    try:
        lim = conn.compute.get_limits().absolute
        return {
            "vcpus":     {"used": lim.get("totalCoresUsed", 0),     "total": lim.get("maxTotalCores", 0)},
            "ram":       {"used": lim.get("totalRAMUsed", 0),        "total": lim.get("maxTotalRAMSize", 0)},
            "instances": {"used": lim.get("totalInstancesUsed", 0), "total": lim.get("maxTotalInstances", 0)},
        }
    except Exception as e:
        return {"error": str(e)}

def get_alarms():
    conn = get_connection()
    try:
        return [{"id": a.alarm_id, "name": a.name, "state": a.state,
                 "enabled": a.is_enabled, "type": a.type,
                 "description": a.description} for a in conn.alarm.alarms()]
    except Exception as e:
        return []

def create_alarm(data):
    conn = get_connection()
    try:
        a = conn.alarm.create_alarm(
            name=data["name"],
            type="gnocchi_aggregation_by_resources_threshold",
            description=data.get("description", ""),
            gnocchi_aggregation_by_resources_threshold_rule={
                "metric": data.get("metric", "cpu"),
                "aggregation_method": "rate:mean",
                "granularity": 300,
                "evaluation_periods": 1,
                "threshold": float(data.get("threshold", 80)),
                "comparison_operator": data.get("operator", "gt"),
                "resource_type": "instance",
                "query": '{"=": {"server_group": ""}}',
            },
            severity=data.get("severity", "moderate"),
        )
        return {"id": a.alarm_id, "name": a.name, "state": a.state}
    except Exception as e:
        return {"error": str(e)}

def delete_alarm(aid):
    conn = get_connection()
    conn.alarm.delete_alarm(aid)
    return {"status": "deleted", "id": aid}

def get_servers_list():
    conn = get_connection()
    try:
        return [{"id": s.id, "name": s.name, "status": s.status,
                 "flavor": s.flavor.get("original_name", s.flavor.get("id", "")),
                 "addresses": {n: [a["addr"] for a in ads] for n, ads in (s.addresses or {}).items()},
                 "created_at": str(s.created_at) if s.created_at else None}
                for s in conn.compute.servers(details=True)]
    except Exception:
        return []

def get_keypairs():
    conn = get_connection()
    try:
        return [{"name": k.name, "fingerprint": k.fingerprint} for k in conn.compute.keypairs()]
    except Exception:
        return []

def get_flavors():
    conn = get_connection()
    try:
        return [{"id": f.id, "name": f.name, "vcpus": f.vcpus, "ram": f.ram, "disk": f.disk}
                for f in sorted(conn.compute.flavors(), key=lambda x: x.ram)]
    except Exception:
        return []

def get_networks():
    conn = get_connection()
    try:
        return [{"id": n.id, "name": n.name, "external": n.is_router_external, "status": n.status}
                for n in conn.network.networks()]
    except Exception:
        return []

def get_images():
    conn = get_connection()
    try:
        return [{"id": i.id, "name": i.name, "status": i.status,
                 "size": i.size, "disk_format": i.disk_format}
                for i in conn.image.images(status="active")]
    except Exception:
        return []
