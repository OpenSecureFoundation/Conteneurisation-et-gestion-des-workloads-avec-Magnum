"""
services/heat_service.py
Service layer pour les stacks Heat hybrides (VM + Cluster Magnum)
"""
from services.openstack_client import get_connection

# Template HOT de base : Stack hybride VM + Cluster Magnum
HYBRID_STACK_TEMPLATE = """
heat_template_version: 2021-04-16
description: Stack hybride - VM classiques + Cluster Magnum

parameters:
  cluster_template_id:
    type: string
    description: ID du cluster template Magnum
  cluster_name:
    type: string
    default: hybrid-cluster
  master_count:
    type: number
    default: 1
  node_count:
    type: number
    default: 2
  vm_flavor:
    type: string
    default: m1.small
  vm_image:
    type: string
    default: cirros-0.5.2-x86_64-disk
  keypair:
    type: string
    description: Nom de la keypair SSH
  network_name:
    type: string
    default: private

resources:
  app_network:
    type: OS::Neutron::Net
    properties:
      name: hybrid-net

  app_subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: app_network }
      cidr: 192.168.100.0/24
      dns_nameservers: [8.8.8.8]

  classic_vm:
    type: OS::Nova::Server
    properties:
      name: hybrid-vm
      flavor: { get_param: vm_flavor }
      image: { get_param: vm_image }
      key_name: { get_param: keypair }
      networks:
        - network: { get_resource: app_network }

  container_cluster:
    type: OS::Magnum::Cluster
    properties:
      name: { get_param: cluster_name }
      cluster_template: { get_param: cluster_template_id }
      master_count: { get_param: master_count }
      node_count: { get_param: node_count }
      keypair: { get_param: keypair }

outputs:
  vm_ip:
    description: IP de la VM classique
    value: { get_attr: [classic_vm, first_address] }
  cluster_id:
    description: ID du cluster Magnum créé
    value: { get_resource: container_cluster }
"""


def list_stacks():
    conn = get_connection()
    stacks = list(conn.orchestration.stacks())
    return [_fmt_stack(s) for s in stacks]


def get_stack(stack_name_or_id):
    conn = get_connection()
    s = conn.orchestration.find_stack(stack_name_or_id)
    if not s:
        return None
    return _fmt_stack(s)


def create_hybrid_stack(data):
    """Crée une stack Heat hybride VM + Cluster Magnum."""
    conn = get_connection()
    parameters = {
        "cluster_template_id": data["cluster_template_id"],
        "cluster_name": data.get("cluster_name", "hybrid-cluster"),
        "master_count": int(data.get("master_count", 1)),
        "node_count": int(data.get("node_count", 2)),
        "vm_flavor": data.get("vm_flavor", "m1.small"),
        "vm_image": data.get("vm_image", "cirros-0.5.2-x86_64-disk"),
        "keypair": data.get("keypair", ""),
        "network_name": data.get("network_name", "private"),
    }
    stack = conn.orchestration.create_stack(
        name=data["stack_name"],
        template=HYBRID_STACK_TEMPLATE,
        parameters=parameters,
        timeout_mins=int(data.get("timeout_mins", 60)),
        disable_rollback=False,
    )
    return _fmt_stack(stack)


def create_custom_stack(data):
    """Crée une stack Heat depuis un template personnalisé fourni par l'utilisateur."""
    conn = get_connection()
    stack = conn.orchestration.create_stack(
        name=data["stack_name"],
        template=data["template"],
        parameters=data.get("parameters", {}),
        timeout_mins=int(data.get("timeout_mins", 60)),
        disable_rollback=data.get("disable_rollback", False),
    )
    return _fmt_stack(stack)


def delete_stack(stack_name_or_id):
    conn = get_connection()
    conn.orchestration.delete_stack(stack_name_or_id)
    return {"status": "deleted", "id": stack_name_or_id}


def get_stack_resources(stack_name_or_id):
    conn = get_connection()
    resources = list(conn.orchestration.resources(stack_name_or_id))
    return [
        {
            "name": r.name,
            "type": r.resource_type,
            "status": r.resource_status,
            "physical_id": r.physical_resource_id,
            "updated_time": str(r.updated_time) if r.updated_time else None,
        }
        for r in resources
    ]


def get_stack_events(stack_name_or_id):
    conn = get_connection()
    events = list(conn.orchestration.events(stack_name_or_id))
    return [
        {
            "resource_name": e.resource_name,
            "status": e.resource_status,
            "reason": e.resource_status_reason,
            "time": str(e.event_time) if e.event_time else None,
        }
        for e in list(events)[-20:]  # derniers 20 events
    ]


def get_hybrid_template():
    """Retourne le template HOT hybride de référence."""
    return HYBRID_STACK_TEMPLATE


def _fmt_stack(s):
    return {
        "id": s.id,
        "name": s.name,
        "status": s.status,
        "status_reason": getattr(s, "status_reason", None),
        "description": getattr(s, "description", None),
        "created_at": str(s.created_at) if getattr(s, "created_at", None) else None,
        "updated_at": str(s.updated_at) if getattr(s, "updated_at", None) else None,
        "outputs": getattr(s, "outputs", []),
        "parameters": getattr(s, "parameters", {}),
    }
