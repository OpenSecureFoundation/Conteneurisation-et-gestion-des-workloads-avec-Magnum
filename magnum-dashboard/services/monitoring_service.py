"""
services/monitoring_service.py
Service de monitoring via Gnocchi (métriques), Ceilometer et Aodh (alarmes)
"""
from services.openstack_client import get_connection
import datetime


def get_dashboard_summary():
    """Résumé global pour le dashboard principal."""
    conn = get_connection()
    try:
        clusters = list(conn.container_infrastructure_management.clusters())
        stacks = list(conn.orchestration.stacks())
        servers = list(conn.compute.servers())
        networks = list(conn.network.networks())

        status_counts = {}
        for c in clusters:
            s = c.status or "UNKNOWN"
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            "clusters": {
                "total": len(clusters),
                "by_status": status_counts,
                "running": sum(1 for c in clusters if c.status == "CREATE_COMPLETE"),
                "creating": sum(1 for c in clusters if "CREATE_IN_PROGRESS" in (c.status or "")),
                "error": sum(1 for c in clusters if "ERROR" in (c.status or "") or "FAILED" in (c.status or "")),
            },
            "stacks": {
                "total": len(stacks),
                "complete": sum(1 for s in stacks if "COMPLETE" in (s.status or "")),
                "failed": sum(1 for s in stacks if "FAILED" in (s.status or "")),
            },
            "compute": {
                "servers": len(servers),
                "active": sum(1 for s in servers if s.status == "ACTIVE"),
            },
            "networks": len(networks),
        }
    except Exception as e:
        return {"error": str(e)}


def get_compute_metrics():
    """Métriques de calcul via Nova (vCPU, RAM, instances)."""
    conn = get_connection()
    try:
        limits = conn.compute.get_limits()
        absolute = limits.absolute
        return {
            "vcpus": {
                "used": absolute.get("totalCoresUsed", 0),
                "total": absolute.get("maxTotalCores", 0),
            },
            "ram": {
                "used": absolute.get("totalRAMUsed", 0),
                "total": absolute.get("maxTotalRAMSize", 0),
            },
            "instances": {
                "used": absolute.get("totalInstancesUsed", 0),
                "total": absolute.get("maxTotalInstances", 0),
            },
        }
    except Exception as e:
        return {"error": str(e)}


def get_alarms():
    """Récupère les alarmes Aodh."""
    conn = get_connection()
    try:
        alarms = list(conn.alarm.alarms())
        return [
            {
                "id": a.alarm_id,
                "name": a.name,
                "state": a.state,
                "enabled": a.is_enabled,
                "type": a.type,
                "description": a.description,
                "created_at": str(a.created_at) if getattr(a, "created_at", None) else None,
            }
            for a in alarms
        ]
    except Exception as e:
        return {"error": str(e), "alarms": []}


def create_alarm(data):
    """Crée une alarme Aodh pour un cluster (CPU usage par exemple)."""
    conn = get_connection()
    try:
        alarm = conn.alarm.create_alarm(
            name=data["name"],
            type="gnocchi_aggregation_by_resources_threshold",
            description=data.get("description", "Alarme créée via MagnumDash"),
            gnocchi_aggregation_by_resources_threshold_rule={
                "metric": data.get("metric", "cpu"),
                "aggregation_method": "rate:mean",
                "granularity": 300,
                "evaluation_periods": 1,
                "threshold": float(data.get("threshold", 80)),
                "comparison_operator": data.get("operator", "gt"),
                "resource_type": "instance",
                "query": data.get("query", '{"=": {"server_group": ""}}'),
            },
            severity=data.get("severity", "moderate"),
            alarm_actions=data.get("alarm_actions", []),
            ok_actions=data.get("ok_actions", []),
        )
        return {"id": alarm.alarm_id, "name": alarm.name, "state": alarm.state}
    except Exception as e:
        return {"error": str(e)}


def delete_alarm(alarm_id):
    conn = get_connection()
    conn.alarm.delete_alarm(alarm_id)
    return {"status": "deleted", "id": alarm_id}


def get_servers_list():
    """Liste toutes les instances Nova avec leurs statuts."""
    conn = get_connection()
    try:
        servers = list(conn.compute.servers(details=True))
        return [
            {
                "id": s.id,
                "name": s.name,
                "status": s.status,
                "flavor": s.flavor.get("original_name", s.flavor.get("id", "")),
                "image": s.image.get("id", "") if s.image else "",
                "addresses": {
                    net: [a["addr"] for a in addrs]
                    for net, addrs in (s.addresses or {}).items()
                },
                "created_at": str(s.created_at) if s.created_at else None,
            }
            for s in servers
        ]
    except Exception as e:
        return []


def get_keypairs():
    """Liste les keypairs disponibles."""
    conn = get_connection()
    try:
        kps = list(conn.compute.keypairs())
        return [{"name": k.name, "fingerprint": k.fingerprint} for k in kps]
    except Exception:
        return []


def get_flavors():
    """Liste les flavors disponibles."""
    conn = get_connection()
    try:
        flavors = list(conn.compute.flavors())
        return [
            {
                "id": f.id,
                "name": f.name,
                "vcpus": f.vcpus,
                "ram": f.ram,
                "disk": f.disk,
            }
            for f in sorted(flavors, key=lambda x: x.ram)
        ]
    except Exception:
        return []


def get_networks():
    """Liste les réseaux Neutron."""
    conn = get_connection()
    try:
        nets = list(conn.network.networks())
        return [
            {
                "id": n.id,
                "name": n.name,
                "external": n.is_router_external,
                "status": n.status,
            }
            for n in nets
        ]
    except Exception:
        return []


def get_images():
    """Liste les images Glance."""
    conn = get_connection()
    try:
        imgs = list(conn.image.images(status="active"))
        return [
            {
                "id": i.id,
                "name": i.name,
                "status": i.status,
                "size": i.size,
                "disk_format": i.disk_format,
            }
            for i in imgs
        ]
    except Exception:
        return []
