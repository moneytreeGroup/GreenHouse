from flask import Blueprint, send_file
import os

image_bp = Blueprint("images", __name__)


@image_bp.route("/plant/<plant_name>")
def get_plant_image(plant_name):
    """Serve plant image by plant name - Simple path: plant_images/plant_name/image.jpg"""
    try:
        folder_name = plant_name.lower().replace(" ", "_")
        current_dir = os.path.dirname(__file__)
        backend_dir = os.path.dirname(current_dir)
        images_dir = os.path.join(backend_dir, "plant_images", folder_name)

        if not os.path.exists(images_dir):
            return f"No images found for {plant_name}", 404

        image_files = [
            f
            for f in os.listdir(images_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
        ]

        if not image_files:
            return f"No image files found for {plant_name}", 404

        image_path = os.path.join(images_dir, image_files[0])
        return send_file(image_path)

    except (OSError, IOError, FileNotFoundError):
        return f"Error loading image for {plant_name}", 500
