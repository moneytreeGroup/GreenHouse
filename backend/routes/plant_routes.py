from flask import Blueprint, request, jsonify
from services.plant_care_service import PlantCareService
from services.image_processor import ImageProcessor
from models.plant_model import PlantModel
import logging

plant_bp = Blueprint("plants", __name__)
plant_care_service = PlantCareService()
image_processor = ImageProcessor()
plant_model = PlantModel()


@plant_bp.route("/identify", methods=["POST"])
def identify_plant():
    """
    Identify a plant from an uploaded image
    Expected: multipart/form-data with 'image' file
    Returns: plant identification results with confidence scores
    """
    try:
        # Check if image file is present
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not image_processor.is_valid_image(file):
            return (
                jsonify(
                    {
                        "error": "Invalid image format. Please upload JPG, PNG, or WebP files."
                    }
                ),
                400,
            )

        # Process the image
        processed_image = image_processor.preprocess_image(file)

        # Get prediction from model
        predictions = plant_model.predict(processed_image)

        # Format response
        response = {
            "success": True,
            "predictions": predictions,
            "message": f"Found {len(predictions)} possible matches",
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in plant identification: {str(e)}")
        return jsonify({"error": "Failed to process image"}), 500


@plant_bp.route("/care/<plant_name>", methods=["GET"])
def get_plant_care(plant_name):
    """
    Get care instructions for a specific plant
    Returns: detailed care information
    """
    try:
        care_data = plant_care_service.get_care_data(plant_name)

        if not care_data:
            return (
                jsonify({"error": f"Care data not found for plant: {plant_name}"}),
                404,
            )

        return jsonify({"success": True, "plant": care_data}), 200

    except Exception as e:
        logging.error(f"Error getting care data: {str(e)}")
        return jsonify({"error": "Failed to retrieve care data"}), 500


@plant_bp.route("/care/search", methods=["GET"])
def search_plants():
    """
    Search for plants by name
    Query parameter: q (search term)
    Returns: list of matching plants
    """
    try:
        search_term = request.args.get("q", "").strip()

        if not search_term:
            return jsonify({"error": "Search term is required"}), 400

        results = plant_care_service.search_plants(search_term)

        return (
            jsonify({"success": True, "results": results, "count": len(results)}),
            200,
        )

    except Exception as e:
        logging.error(f"Error searching plants: {str(e)}")
        return jsonify({"error": "Failed to search plants"}), 500


@plant_bp.route("/list", methods=["GET"])
def list_plants():
    """
    Get list of all available plants
    Returns: list of all plants with basic info
    """
    try:
        plants = plant_care_service.get_all_plants()

        return jsonify({"success": True, "plants": plants, "count": len(plants)}), 200

    except Exception as e:
        logging.error(f"Error listing plants: {str(e)}")
        return jsonify({"error": "Failed to retrieve plant list"}), 500


@plant_bp.route("/identify-and-care", methods=["POST"])
def identify_and_get_care():
    """
    Combined endpoint: identify plant and return care instructions
    Expected: multipart/form-data with 'image' file
    Returns: plant identification + care data for top match
    """
    try:
        # Check if image file is present
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not image_processor.is_valid_image(file):
            return (
                jsonify(
                    {
                        "error": "Invalid image format. Please upload JPG, PNG, or WebP files."
                    }
                ),
                400,
            )

        # Process the image and get predictions
        processed_image = image_processor.preprocess_image(file)
        predictions = plant_model.predict(processed_image)

        if not predictions:
            return jsonify({"error": "Could not identify the plant"}), 404

        # Get care data for the top prediction
        top_prediction = predictions[0]
        care_data = plant_care_service.get_care_data(top_prediction["name"])

        response = {
            "success": True,
            "identification": {"predictions": predictions, "top_match": top_prediction},
            "care_data": care_data,
            "message": f'Identified as {top_prediction["name"]} with {top_prediction["confidence"]:.1%} confidence',
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error in identify and care: {str(e)}")
        return jsonify({"error": "Failed to process request"}), 500
