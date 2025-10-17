from flask import Blueprint, request, jsonify
from services.plant_care_service import PlantCareService
from services.image_processor import ImageProcessor
from models.plant_model import PlantModel
import logging
import os

plant_bp = Blueprint("plants", __name__)
plant_care_service = PlantCareService()
image_processor = ImageProcessor()

# Load your trained model
model_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "plant_cnn_complete_model.pth"
)
plant_model = PlantModel(num_classes=19)
plant_model.class_names = [
    "anthurium",
    "aloe",
    "bird of paradise",
    "chinese evergreen",
    "ctenanthe",
    "dracaena",
    "dieffenbachia",
    "ficus",
    "ivy",
    "money tree",
    "monstera",
    "peace lily",
    "poinsettia",
    "hypoestes",
    "pothos",
    "schefflera",
    "snake plant",
    "maranta",
    "zamioculcas zamiifolia",
]
plant_model.load_model(model_path)


@plant_bp.route("/identify", methods=["POST"])
def identify_plant():
    """
    Identify a plant from an uploaded image
    Expected: multipart/form-data with 'image' file
    Returns: care data for the best match
    """
    print("Received identify request")
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
        if not predictions:
            return jsonify({"error": "Could not identify the plant"}), 404
        print("Predictions:", predictions)
        # Find the top match (highest confidence)
        top_prediction = max(predictions, key=lambda x: x["confidence"])
        plant_name = top_prediction["name"]

        # Get care data for the best match
        care_data = plant_care_service.get_care_data(plant_name)

        if not care_data:
            return (
                jsonify({"error": f"Care data not found for plant: {plant_name}"}),
                404,
            )

        # Add confidence score to care data
        care_data_with_confidence = dict(care_data)
        care_data_with_confidence["confidence"] = top_prediction["confidence"]

        return jsonify({"success": True, "plant": care_data_with_confidence}), 200

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


@plant_bp.route("/model/info", methods=["GET"])
def get_model_info():
    """
    Get information about the loaded model (for debugging)
    """
    try:
        model_info = plant_model.get_model_info()
        return jsonify({"success": True, "model_info": model_info}), 200
    except Exception as e:
        logging.error(f"Error getting model info: {str(e)}")
        return jsonify({"error": "Failed to get model info"}), 500
