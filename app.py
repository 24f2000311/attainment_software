from flask import Flask
from Controllers import main_bp, attainment_bp, cqi_bp, reports_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(attainment_bp)
app.register_blueprint(cqi_bp)
app.register_blueprint(reports_bp)

if __name__ == '__main__':
    app.run(port=6000,debug=True)
