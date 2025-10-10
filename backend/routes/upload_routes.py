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
        # Check if image file is present
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type. Please upload JPG, PNG, or WebP files."
                    }
                ),
                400,
            )

        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # Save file temporarily
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Get file info
        file_size = os.path.getsize(file_path)

        # Validate image can be processed
        try:
            image_info = image_processor.get_image_info(file_path)
        except Exception as e:
            # Clean up invalid file
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


@upload_bp.route("/validate", methods=["POST"])
def validate_image():
    """
    Validate an image without saving it
    Expected: multipart/form-data with 'image' file
    Returns: validation result and image info
    """
    try:
        # Check if image file is present
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file type. Please upload JPG, PNG, or WebP files."
                    }
                ),
                400,
            )

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
        if file_size > max_size:
            return (
                jsonify(
                    {
                        "error": f"File too large. Maximum size is {max_size // (1024*1024)}MB."
                    }
                ),
                400,
            )

        # Validate image can be processed
        try:
            image_info = image_processor.validate_image_stream(file)
            file.seek(0)  # Reset for potential future use
        except Exception as e:
            return jsonify({"error": "Invalid image file or corrupted data"}), 400

        response = {
            "success": True,
            "valid": True,
            "file_info": {
                "original_name": file.filename,
                "size": file_size,
                "dimensions": image_info,
            },
            "message": "Image is valid and ready for processing",
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error validating image: {str(e)}")
        return jsonify({"error": "Failed to validate image"}), 500


@upload_bp.route("/cleanup", methods=["POST"])
def cleanup_temp_files():
    """
    Clean up temporary uploaded files
    Expected: JSON with file paths to clean
    """
    try:
        data = request.get_json()
        if not data or "files" not in data:
            return jsonify({"error": "No files specified for cleanup"}), 400

        files_cleaned = 0
        upload_folder = current_app.config["UPLOAD_FOLDER"]

        for filename in data["files"]:
            try:
                # Security check - ensure file is in upload folder
                file_path = os.path.join(upload_folder, secure_filename(filename))
                if os.path.exists(file_path) and upload_folder in os.path.abspath(
                    file_path
                ):
                    os.remove(file_path)
                    files_cleaned += 1
            except Exception as e:
                logging.warning(f"Could not clean file {filename}: {str(e)}")
                continue

        return (
            jsonify(
                {
                    "success": True,
                    "files_cleaned": files_cleaned,
                    "message": f"Cleaned up {files_cleaned} temporary files",
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Error cleaning up files: {str(e)}")
        return jsonify({"error": "Failed to cleanup files"}), 500
