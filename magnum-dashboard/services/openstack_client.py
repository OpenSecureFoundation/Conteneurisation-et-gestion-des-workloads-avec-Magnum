"""
services/openstack_client.py
Gestion de la connexion OpenStack via openstacksdk
"""
import openstack
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Retourne une connexion OpenStack authentifiée via openstacksdk."""
    conn = openstack.connect(
        auth_url=os.getenv("OS_AUTH_URL"),
        project_name=os.getenv("OS_PROJECT_NAME"),
        username=os.getenv("OS_USERNAME"),
        password=os.getenv("OS_PASSWORD"),
        user_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
        project_domain_name=os.getenv("OS_PROJECT_DOMAIN_NAME", "Default"),
        region_name=os.getenv("OS_REGION_NAME", "RegionOne"),
    )
    return conn
