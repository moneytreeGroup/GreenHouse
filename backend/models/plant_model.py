import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
import logging


class PlantModel:
    """
    PyTorch model wrapper for plant identification
    This is a placeholder structure - replace with your trained model
    """

    def __init__(self, model_path: str = None, device: str = None):
        """
        Initialize plant identification model

        Args:
            model_path: Path to trained model file
            device: Device to run inference on ('cpu', 'cuda', 'mps')
        """
        self.device = self._get_device(device)
        self.model = None
        self.class_names = []
        self.model_path = model_path
        self.is_loaded = False

        # Define transforms for preprocessing
        self.transforms = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),  # ImageNet normalization
            ]
        )

        # Plant names that your model can identify
        # Update this list with your actual trained classes
        self.plant_classes = [
            "anthurium",
            "aloe",
            "alocasia",
            "begonia",
            "bird of paradise",
            "calathea",
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
            "yucca",
            "zamioculcas zamiifolia",
        ]

        # Try to load model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def _get_device(self, device: str = None) -> torch.device:
        """Determine the best device for inference"""
        if device:
            return torch.device(device)

        if torch.cuda.is_available():
            return torch.device("cuda")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")  # Apple Silicon
        else:
            return torch.device("cpu")

    def create_model(self, num_classes: int, pretrained: bool = True) -> nn.Module:
        """
        Create a model architecture for plant classification
        You can replace this with your custom architecture
        """
        # Using ResNet50 as base - modify as needed
        model = models.resnet50(pretrained=pretrained)

        # Replace the final layer for your number of plant classes
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, num_classes)

        return model

    def load_model(self, model_path: str) -> bool:
        """Load trained model from file"""
        try:
            # Load model checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)

            # Create model architecture
            num_classes = len(self.plant_classes)
            self.model = self.create_model(num_classes, pretrained=False)

            # Load state dict
            if "model_state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["model_state_dict"])
            else:
                self.model.load_state_dict(checkpoint)

            # Load class names if available
            if "class_names" in checkpoint:
                self.class_names = checkpoint["class_names"]
            else:
                self.class_names = self.plant_classes

            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True

            logging.info(f"Model loaded successfully from {model_path}")
            logging.info(f"Device: {self.device}")
            logging.info(f"Number of classes: {len(self.class_names)}")

            return True

        except Exception as e:
            logging.error(f"Failed to load model: {str(e)}")
            self.is_loaded = False
            return False

    def predict(self, image_array: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Predict plant species from preprocessed image

        Args:
            image_array: Preprocessed image as numpy array
            top_k: Number of top predictions to return

        Returns:
            List of predictions with confidence scores
        """
        if not self.is_loaded:
            # Return mock predictions for development
            return self._mock_predictions(top_k)

        try:
            # Convert numpy array to tensor
            if image_array.ndim == 4:  # Remove batch dimension if present
                image_array = image_array[0]

            # Convert to tensor and add batch dimension
            image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).float()
            image_tensor = image_tensor.unsqueeze(0).to(self.device)

            # Run inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)

                # Get top k predictions
                top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)

                predictions = []
                for i in range(top_k):
                    class_idx = top_indices[0][i].item()
                    confidence = top_probs[0][i].item()

                    if class_idx < len(self.class_names):
                        plant_name = self.class_names[class_idx]
                        predictions.append(
                            {
                                "name": plant_name,
                                "confidence": confidence,
                                "class_index": class_idx,
                            }
                        )

                return predictions

        except Exception as e:
            logging.error(f"Prediction failed: {str(e)}")
            return self._mock_predictions(top_k)

    def _mock_predictions(self, top_k: int = 5) -> List[Dict]:
        """
        Return mock predictions for development/testing
        Remove this when you have a trained model
        """
        import random

        # Simulate realistic confidence scores
        mock_predictions = []
        available_plants = self.plant_classes.copy()

        for i in range(min(top_k, len(available_plants))):
            plant = random.choice(available_plants)
            available_plants.remove(plant)

            # Generate decreasing confidence scores
            if i == 0:
                confidence = random.uniform(
                    0.7, 0.95
                )  # High confidence for top prediction
            elif i == 1:
                confidence = random.uniform(0.4, 0.7)  # Medium confidence
            else:
                confidence = random.uniform(0.1, 0.4)  # Lower confidence

            mock_predictions.append(
                {
                    "name": plant,
                    "confidence": confidence,
                    "class_index": self.plant_classes.index(plant),
                    "mock": True,  # Indicate this is a mock prediction
                }
            )

        # Sort by confidence
        mock_predictions.sort(key=lambda x: x["confidence"], reverse=True)

        logging.info("Returning mock predictions (no model loaded)")
        return mock_predictions

    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "is_loaded": self.is_loaded,
            "model_path": self.model_path,
            "device": str(self.device),
            "num_classes": len(self.class_names),
            "class_names": self.class_names,
            "model_type": "ResNet50" if self.model else "None",
        }

    def validate_prediction(self, prediction: Dict) -> bool:
        """Validate a prediction result"""
        required_fields = ["name", "confidence", "class_index"]

        if not all(field in prediction for field in required_fields):
            return False

        if not isinstance(prediction["confidence"], (int, float)):
            return False

        if not 0 <= prediction["confidence"] <= 1:
            return False

        return True

    def preprocess_for_model(self, image_array: np.ndarray) -> torch.Tensor:
        """
        Additional preprocessing specifically for the model
        Override this method if your model needs different preprocessing
        """
        try:
            # Convert numpy array to PIL Image for transforms
            if image_array.ndim == 4:  # Remove batch dimension
                image_array = image_array[0]

            # Denormalize if needed (assuming input is 0-1 normalized)
            if image_array.max() <= 1:
                image_array = (image_array * 255).astype(np.uint8)

            # Apply transforms
            tensor = self.transforms(image_array)
            tensor = tensor.unsqueeze(0)  # Add batch dimension

            return tensor.to(self.device)

        except Exception as e:
            logging.error(f"Model preprocessing failed: {str(e)}")
            raise ValueError(f"Failed to preprocess image for model: {str(e)}")

    def get_class_distribution(self) -> Dict[str, float]:
        """
        Get the distribution of classes (useful for model analysis)
        This is a placeholder - implement based on your training data
        """
        # Equal distribution for mock
        if not self.class_names:
            return {}

        equal_prob = 1.0 / len(self.class_names)
        return {name: equal_prob for name in self.class_names}

    def set_confidence_threshold(self, threshold: float = 0.5) -> None:
        """Set minimum confidence threshold for predictions"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))

    def filter_predictions_by_confidence(
        self, predictions: List[Dict], threshold: float = 0.3
    ) -> List[Dict]:
        """Filter predictions by confidence threshold"""
        return [pred for pred in predictions if pred["confidence"] >= threshold]
