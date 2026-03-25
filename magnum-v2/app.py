import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, session, redirect, url_for, request
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv(override=False)

from routes.auth import bp as auth_bp
from routes.clusters import bp as clusters_bp
from routes.templates import bp as templates_bp
from routes.api import sb as stacks_bp, mb as monitoring_bp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "magnum-dash-2025")
app.permanent_session_lifetime = timedelta(hours=8)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(clusters_bp)
app.register_blueprint(templates_bp)
app.register_blueprint(stacks_bp)
app.register_blueprint(monitoring_bp)

@app.before_request
def require_login():
    public = {"auth.login", "auth.logout", "static"}
    if request.endpoint in public:
        return None
    if not session.get("authenticated"):
        return redirect(url_for("auth.login", next=request.url))

@app.context_processor
def inject_user():
    return {"current_user": session.get("username", ""), "current_project": session.get("project_name", "")}

@app.route("/")
def index(): return render_template("index.html")

@app.route("/clusters")
def clusters_page(): return render_template("clusters.html")

@app.route("/templates")
def templates_page(): return render_template("cluster_templates.html")

@app.route("/stacks")
def stacks_page(): return render_template("stacks.html")

@app.route("/monitoring")
def monitoring_page(): return render_template("monitoring.html")

@app.errorhandler(404)
def not_found(e): return jsonify({"error": "Non trouvé"}), 404

@app.errorhandler(500)
def server_error(e): return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 8080))
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    print(f"\n🚀  MagnumDash → http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)
