from flask import Flask
from Controllers import main_bp, attainment_bp, cqi_bp, reports_bp
from services.state import resource_path

app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(attainment_bp)
app.register_blueprint(cqi_bp)
app.register_blueprint(reports_bp)

if __name__ == "__main__":
    app.run(
        port=5000,
        debug=False,   # IMPORTANT for EXE
        use_reloader=False
    )
