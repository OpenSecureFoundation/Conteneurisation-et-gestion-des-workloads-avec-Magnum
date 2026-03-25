import openstack, os
from dotenv import load_dotenv
load_dotenv(override=False)

def get_connection():
    return openstack.connect(
        auth_url=os.getenv("OS_AUTH_URL", "http://controller:5000/v3"),
        project_name=os.getenv("OS_PROJECT_NAME", "admin"),
        username=os.getenv("OS_USERNAME", "admin"),
        password=os.getenv("OS_PASSWORD", "ADMIN_PASS"),
        user_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
        project_domain_name=os.getenv("OS_PROJECT_DOMAIN_NAME", "Default"),
        region_name=os.getenv("OS_REGION_NAME", "RegionOne"),
    )
