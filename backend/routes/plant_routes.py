from flask import Blueprint, request, jsonify
from services.plant_care_service import PlantCareService
from services.image_processor import ImageProcessor
import logging
import os
import requests


plant_bp = Blueprint("plants", __name__)
plant_care_service = PlantCareService()
image_processor = ImageProcessor()

HF_MODEL_URL = os.environ.get("HF_MODEL_URL")


def predict_with_hf_api(image_file):
    """Send image to Hugging Face Gradio API for prediction"""
    try:
        if not HF_MODEL_URL:
            raise Exception("HF_MODEL_URL not configured")

        print(f"Calling API URL: {HF_MODEL_URL}")

        # Reset file pointer
        image_file.seek(0)

        # For Gradio API, send the file directly without converting to PIL
        files = {
            "data": (
                image_file.filename or "image.jpg",
                image_file.stream,
                image_file.content_type or "image/jpeg",
            )
        }

        response = requests.post(HF_MODEL_URL, files=files, timeout=30)

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:300]}")  # Debug log

        if response.status_code == 200:
            result = response.json()
            print(f"Parsed JSON: {result}")

            if result.get("success"):
                return result.get("predictions", [])
            else:
                # Sometimes Gradio returns results in different format
                if isinstance(result, list) and len(result) > 0:
                    # If result is directly the predictions array
                    return result
                elif isinstance(result, dict) and "predictions" in result:
                    return result["predictions"]
                else:
                    logging.error(f"Unexpected response format: {result}")
        else:
            logging.error(f"HF API error: {response.status_code} - {response.text}")

        return []
    except Exception as e:
        logging.error(f"HF API error: {e}")
        return []


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

        if HF_MODEL_URL:
            print("Using Hugging Face API for prediction")
            predictions = predict_with_hf_api(file)

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
    Get information about the Hugging Face Gradio Space
    """
    try:
        model_info = {
            "service": "Hugging Face Gradio Space",
            "hf_url_configured": bool(HF_MODEL_URL),
            "model_url": HF_MODEL_URL if HF_MODEL_URL else "Not configured",
        }

        if HF_MODEL_URL:
            try:
                space_url = HF_MODEL_URL.replace("/api/predict", "")
                response = requests.get(space_url, timeout=10)

                model_info["hf_status"] = (
                    "connected" if response.status_code == 200 else "disconnected"
                )
                model_info["response_code"] = response.status_code

                if response.status_code == 200:
                    model_info["space_status"] = "running"
                else:
                    model_info["space_status"] = "not_running"

            except requests.exceptions.Timeout:
                model_info["hf_status"] = "timeout"
                model_info["space_status"] = "timeout"
            except Exception as e:
                model_info["hf_status"] = "error"
                model_info["error"] = str(e)
        else:
            model_info["hf_status"] = "not_configured"

        return jsonify({"success": True, "model_info": model_info}), 200
    except Exception as e:
        logging.error(f"Error getting model info: {str(e)}")
        return jsonify({"error": "Failed to get model info"}), 500
