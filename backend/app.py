from flask import Flask
from flask_cors import CORS
import os
from routes.plant_routes import plant_bp
from routes.upload_routes import upload_bp


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    app.config["UPLOAD_FOLDER"] = "uploads"

    # Create upload directory if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Enable CORS for React frontend
    CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])

    # Register blueprints
    app.register_blueprint(plant_bp, url_prefix="/api/plants")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")

    @app.route("/")
    def health_check():
        return {"status": "Plant Recognition API is running!", "version": "1.0.0"}

    @app.errorhandler(413)
    def too_large(e):
        return {"error": "File too large. Maximum size is 16MB."}, 413

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Endpoint not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(
        os.environ.get("PORT", 8000)
    )  # Default to 8000, override with PORT env var
    app.run(debug=True, host="0.0.0.0", port=port)
