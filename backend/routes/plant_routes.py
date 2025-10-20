from flask import Blueprint, request, jsonify
from services.plant_care_service import PlantCareService
from services.image_processor import ImageProcessor
from models.plant_model import PlantModel
import logging
import os

plant_bp = Blueprint("plants", __name__)
plant_care_service = PlantCareService()
image_processor = ImageProcessor()

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
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not image_processor.is_valid_image(file):
            return (
                jsonify(
                    {
                        "error": "Invalid image format. Please upload JPG, PNG, or WebP files."
                    }
                ),
                400,
            )

        processed_image = image_processor.preprocess_image(file)

        predictions = plant_model.predict(processed_image, top_k=5)
        if not predictions:
            return jsonify({"error": "Could not identify the plant"}), 404

        top_prediction = max(predictions, key=lambda x: x["confidence"])
        plant_name = top_prediction["name"]

        care_data = plant_care_service.get_care_data(plant_name)

        if not care_data:
            return (
                jsonify({"error": f"Care data not found for plant: {plant_name}"}),
                404,
            )

        care_data_with_confidence = dict(care_data)
        care_data_with_confidence["confidence"] = top_prediction["confidence"]

        all_predictions_with_care = []
        for prediction in predictions:
            pred_care_data = plant_care_service.get_care_data(prediction["name"])
            if pred_care_data:
                enriched_prediction = {
                    "name": prediction["name"],
                    "confidence": prediction["confidence"],
                    "care": pred_care_data.get("care", {}),
                    "url": pred_care_data.get("url", ""),
                }
                all_predictions_with_care.append(enriched_prediction)

        return (
            jsonify(
                {
                    "success": True,
                    "plant": care_data_with_confidence,
                    "all_predictions": all_predictions_with_care,
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Error in plant identification: {str(e)}")
        return jsonify({"error": "Failed to process image"}), 500


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
