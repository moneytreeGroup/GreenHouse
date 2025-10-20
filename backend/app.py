from flask import Flask
from flask_cors import CORS
import os
from routes.plant_routes import plant_bp
from routes.upload_routes import upload_bp
from routes.image_routes import image_bp


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = "uploads"

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(
        app,
        origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:5174",
        ],
    )

    app.register_blueprint(plant_bp, url_prefix="/api/plants")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(image_bp, url_prefix="/api/images")

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
    port = int(os.environ.get("PORT", 8000))
    app.run(debug=True, host="0.0.0.0", port=port)
