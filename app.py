from flask import Flask, request, redirect, url_for, render_template
from Controllers import main_bp, attainment_bp, cqi_bp, reports_bp, activation_bp
from services.state import resource_path
from services.license_service import LicenseService
import mimetypes
import os
import dotenv
# Load .env from the bundled resource path (works in EXE)
dotenv.load_dotenv(resource_path(".env"))

# Fix for CSS not loading in frozen app
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)
app.secret_key = os.getenv("FLASK_SECRET")  # Required for sessions/flash messages

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(attainment_bp)
app.register_blueprint(cqi_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(activation_bp)

@app.before_request
def check_license():
    # Allow static resources (css, js) and the activation page itself
    if request.path.startswith('/static') or request.path.startswith('/activate'):
        return None
        
    # Check if activated
    if not LicenseService.is_activated():
        return redirect(url_for('activation_bp.activate'))

@app.context_processor
def inject_license_status():
    return dict(is_activated=LicenseService.is_activated())

@app.errorhandler(Exception)
def handle_exception(e):
    """Global Error Handler to prevent app crashes."""
    # In a real app, you might want to log this to a file
    return render_template('error.html', error_message=str(e)), 500

if __name__ == "__main__":
    app.run(
        port=5000,
        debug=True,   # IMPORTANT for EXE
        use_reloader=False
    )
