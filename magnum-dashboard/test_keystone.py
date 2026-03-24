"""
Script de diagnostic Keystone - à exécuter sur le Controller
"""
import openstack
import os

# Valeurs à tester directement
AUTH_URL = "http://127.0.0.1:5000/v3"
USERNAME = "admin"
PASSWORD = "adminpass"  # changez ici si besoin
PROJECT_NAME = "admin"

print("=" * 60)
print("DIAGNOSTIC KEYSTONE")
print("=" * 60)
print(f"AUTH_URL     : {AUTH_URL}")
print(f"USERNAME     : {USERNAME}")
print(f"PROJECT_NAME : {PROJECT_NAME}")
print()

try:
    print("[1] Tentative de connexion openstacksdk...")
    conn = openstack.connect(
        auth_url=AUTH_URL,
        project_name=PROJECT_NAME,
        username=USERNAME,
        password=PASSWORD,
        user_domain_name="Default",
        project_domain_name="Default",
    )
    print("    ✓ objet Connection créé")

    print("[2] Récupération du token...")
    token = conn.auth_token
    print(f"    ✓ token = {str(token)[:30]}...")

    print("[3] Type de conn :", type(conn))
    print("[4] Attributs auth disponibles :")
    for attr in ["auth_ref", "get_token", "_session", "session"]:
        print(f"    - {attr} : {hasattr(conn, attr)}")

    print("[5] Tentative conn.identity.get_token()...")
    try:
        t = conn.identity.get_token()
        print(f"    ✓ token via identity : {str(t)[:30]}")
    except Exception as e2:
        print(f"    ✗ {e2}")

    print("[6] Tentative conn.session.get_token()...")
    try:
        t2 = conn.session.get_token()
        print(f"    ✓ token via session : {str(t2)[:30]}")
        print(f"    ✓ user_id via session.auth.get_access(session).user_id")
    except Exception as e3:
        print(f"    ✗ {e3}")

    print()
    print("✓ CONNEXION RÉUSSIE")

except Exception as e:
    print(f"✗ ERREUR : {e}")

