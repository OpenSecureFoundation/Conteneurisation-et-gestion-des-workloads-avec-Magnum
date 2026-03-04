"""
app.py  –  Point d'entrée principal de MagnumDash
Application Flask pour la gestion OpenStack Magnum + Heat
"""
import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, session, redirect, url_for, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# ── Import des blueprints ──────────────────────────────────────
from routes.auth import bp as auth_bp
from routes.clusters import bp as clusters_bp
from routes.templates import bp as templates_bp
from routes.stacks import bp as stacks_bp
from routes.monitoring import bp as monitoring_bp

# ── Création de l'application ──────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "magnum-dash-secret-change-in-production")
app.permanent_session_lifetime = timedelta(hours=8)
CORS(app)

# ── Enregistrement des blueprints ──────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(clusters_bp)
app.register_blueprint(templates_bp)
app.register_blueprint(stacks_bp)
app.register_blueprint(monitoring_bp)


# ── Middleware : protection de toutes les routes ───────────────
@app.before_request
def require_login():
    """Vérifie que l'utilisateur est authentifié avant chaque requête."""
    public_endpoints = {"auth.login", "auth.logout", "static"}
    if request.endpoint in public_endpoints:
        return None
    if not session.get("authenticated"):
        return redirect(url_for("auth.login", next=request.url))
    return None


# ── Injection des données utilisateur dans tous les templates ──
@app.context_processor
def inject_user():
    """Rend les infos session disponibles dans tous les templates Jinja2."""
    return {
        "current_user": session.get("username", ""),
        "current_project": session.get("project_name", ""),
    }


# ── Routes des pages HTML ──────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clusters")
def clusters_page():
    return render_template("clusters.html")

@app.route("/templates")
def templates_page():
    return render_template("cluster_templates.html")

@app.route("/stacks")
def stacks_page():
    return render_template("stacks.html")

@app.route("/monitoring")
def monitoring_page():
    return render_template("monitoring.html")


# ── Gestion des erreurs ────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ressource non trouvée"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erreur interne du serveur", "detail": str(e)}), 500


# ── Lancement ──────────────────────────────────────────────────
if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 8080))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    print(f"\n🚀 MagnumDash démarré sur http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)
