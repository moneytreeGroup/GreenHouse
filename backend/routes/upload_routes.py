from flask import Blueprint, request, jsonify, current_app
import os
import uuid
from werkzeug.utils import secure_filename
from services.image_processor import ImageProcessor
import logging

upload_bp = Blueprint("upload", __name__)
image_processor = ImageProcessor()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/image", methods=["POST"])
def upload_image():
    """
    Upload and validate an image file
    Expected: multipart/form-data with 'image' file
    Returns: file info and temporary URL
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type. Please upload JPG, PNG, or WebP files."
                    }
                ),
                400,
            )

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        file_size = os.path.getsize(file_path)

        try:
            image_info = image_processor.get_image_info(file_path)
        except Exception as e:
            os.remove(file_path)
            return jsonify({"error": "Invalid image file or corrupted data"}), 400

        response = {
            "success": True,
            "file_info": {
                "filename": unique_filename,
                "original_name": filename,
                "size": file_size,
                "dimensions": image_info,
                "path": file_path,
            },
            "message": "Image uploaded successfully",
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error uploading image: {str(e)}")
        return jsonify({"error": "Failed to upload image"}), 500
