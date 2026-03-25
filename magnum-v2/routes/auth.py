from flask import Blueprint, render_template, request, redirect, url_for, session
import openstack, openstack.exceptions, os
from dotenv import load_dotenv
load_dotenv(override=False)

bp = Blueprint("auth", __name__)

def _try_auth(username, password):
    auth_url = os.getenv("OS_AUTH_URL", "http://controller:5000/v3")
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
        token = conn.auth_token or conn.session.get_token()
        if not token:
            return False, "Impossible d'obtenir un token Keystone."
        try:
            user_id = conn.current_user_id
        except Exception:
            user_id = username
        return True, {
            "username": username,
            "user_id": user_id,
            "project_name": os.getenv("OS_PROJECT_NAME", "admin"),
        }
    except openstack.exceptions.HttpException as e:
        msg = str(e)
        if "401" in msg or "Unauthorized" in msg:
            return False, "Identifiant ou mot de passe incorrect."
        return False, f"Erreur Keystone : {msg[:100]}"
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
            error = "Identifiant et mot de passe requis."
        else:
            ok, result = _try_auth(username, password)
            if ok:
                session.permanent = True
                session["authenticated"] = True
                session["username"] = result["username"]
                session["project_name"] = result["project_name"]
                session["user_id"] = result.get("user_id", "")
                return redirect(request.args.get("next", url_for("index")))
            else:
                error = result
    return render_template("login.html", error=error)

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
