"""
routes/auth.py  –  Authentification via OpenStack Keystone
Basé sur le diagnostic : conn.auth_token et conn.session.get_token() fonctionnent
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
import openstack
import openstack.exceptions
import os
from dotenv import load_dotenv

load_dotenv(override=False)

bp = Blueprint("auth", __name__)


def _get_auth_url():
    url = os.getenv("OS_AUTH_URL", "").strip()
    if url:
        return url
    return "http://127.0.0.1:5000/v3"


def _try_keystone_auth(username, password):
    """
    Authentification Keystone — méthode validée par diagnostic :
    - conn.auth_token         → token OK
    - conn.session.get_token()→ token OK
    - conn.current_user_id    → user_id
    - conn.current_project_id → project_id
    """
    auth_url = _get_auth_url()

    try:
        conn = openstack.connect(
            auth_url=auth_url,
            project_name=os.getenv("OS_PROJECT_NAME", "admin"),
            username=username,
            password=password,
            user_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
            project_domain_name=os.getenv("OS_PROJECT_DOMAIN_NAME", "Default"),
            region_name=os.getenv("OS_REGION_NAME", "RegionOne"),
        )

        # Récupération du token (méthode confirmée par diagnostic)
        token = conn.auth_token
        if not token:
            token = conn.session.get_token()

        if not token:
            return False, "Authentification échouée : impossible d'obtenir un token."

        # Récupération user_id / project_id
        try:
            user_id = conn.current_user_id
        except Exception:
            user_id = username

        try:
            project_id = conn.current_project_id
        except Exception:
            project_id = os.getenv("OS_PROJECT_NAME", "admin")

        return True, {
            "username": username,
            "user_id": user_id,
            "project_id": project_id,
            "project_name": os.getenv("OS_PROJECT_NAME", "admin"),
        }

    except openstack.exceptions.HttpException as e:
        msg = str(e)
        if "401" in msg or "Unauthorized" in msg:
            return False, "Identifiant ou mot de passe incorrect."
        if "404" in msg:
            return False, f"Keystone introuvable à : {auth_url}"
        return False, f"Erreur HTTP : {msg[:120]}"

    except Exception as e:
        msg = str(e)
        if "Connection refused" in msg or "Failed to establish" in msg:
            return False, f"Keystone inaccessible sur {auth_url}"
        return False, f"Erreur : {msg[:150]}"


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Veuillez renseigner le nom d'utilisateur et le mot de passe."
        else:
            success, result = _try_keystone_auth(username, password)
            if success:
                session.permanent = True
                session["authenticated"] = True
                session["username"]     = result["username"]
                session["project_name"] = result["project_name"]
                session["user_id"]      = result.get("user_id", "")
                return redirect(request.args.get("next", url_for("index")))
            else:
                error = result

    return render_template("login.html", error=error)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
