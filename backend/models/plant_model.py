import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
import logging
import torch.nn.functional as F
from PIL import Image


class PlantModel(nn.Module):
    """
    PyTorch model for plant identification (matches SmallCNN2 checkpoint structure)
    5-layer CNN for plant species classification
    - 5 convolutional blocks with batch normalization
    - Gradual channel progression
    - Single FC layer with dropout for regularization
    """

    def __init__(self, num_classes=None):
        super().__init__()
        if num_classes is None:
            num_classes = 29  # Update to 29 classes
        # 5 Convolutional blocks with gradual progression
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 96, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(96)
        self.conv3 = nn.Conv2d(96, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.conv4 = nn.Conv2d(128, 192, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(192)
        self.conv5 = nn.Conv2d(192, 256, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(256)
        # Pooling layers
        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((6, 6))
        # Single FC layer to prevent overfitting
        self.fc1 = nn.Linear(256 * 6 * 6, 512)
        self.dropout = nn.Dropout(0.6)
        self.fc2 = nn.Linear(512, num_classes)
        self.class_names = []
        self.is_loaded = False
        self.confidence_threshold = 0.5

        # Define transforms for preprocessing
        self.transforms = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),  # ImageNet normalization
            ]
        )

        # Plant names that your model can identify
        # Correct order as provided
        self.plant_classes = [
            "Ivy",
            "Schefflera",
            "Pothos",
            "Peace Lily",
            "Poinsettia",
            "Zamioculcas Zamiifolia 'ZZ'",
            "Ctenanthe",
            "Hypoestes",
            "Anthurium",
            "Aloe",
            "Dracaena",
            "Chinese Evergreen",
            "Maranta",
            "Monstera",
            "Dieffenbachia",
            "Money Tree",
            "Ficus",
            "Bird of Paradise",
            "Snake Plant",
        ]
        self.class_names = self.plant_classes

    def forward(self, x):
        # Convolutional blocks with BatchNorm and ReLU
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        x = self.pool(F.relu(self.bn5(self.conv5(x))))
        # Adaptive pooling
        x = self.adaptive_pool(x)
        # Flatten and fully connected layers
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

    def get_feature_maps(self, x):
        """Return intermediate feature maps for visualization"""
        features = []
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        features.append(x)
        x = self.pool(F.relu(self.bn5(self.conv5(x))))
        features.append(x)
        return features

    def save_model(self, path):
        torch.save(self.state_dict(), path)

    def load_model(self, path, device=None):
        if device is None:
            device = "cpu"
        checkpoint = torch.load(path, map_location=device)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
            # Extract class names if present
            if "class_names" in checkpoint:
                self.class_names = checkpoint["class_names"]
                self.plant_classes = checkpoint["class_names"]
        else:
            state_dict = checkpoint
        # Remove fc2 weights if shape mismatch
        own_state = self.state_dict()
        filtered_state_dict = {
            k: v
            for k, v in state_dict.items()
            if k in own_state and own_state[k].shape == v.shape
        }
        missing = [k for k in own_state if k not in filtered_state_dict]
        if missing:
            logging.warning(
                f"Skipping loading of layers due to shape mismatch or missing: {missing}"
            )
        own_state.update(filtered_state_dict)
        self.load_state_dict(own_state)
        self.is_loaded = True
        self.eval()

    def predict(self, image_input, top_k: int = 5) -> List[Dict]:
        """
        Predict plant species from preprocessed image (PIL Image only)

        Args:
            image_input: Preprocessed image as PIL Image
            top_k: Number of top predictions to return

        Returns:
            List of predictions with confidence scores
        """
        if not self.is_loaded:
            raise RuntimeError("Model is not loaded. Cannot make predictions.")

        try:
            # Ensure input is a PIL Image
            if not isinstance(image_input, Image.Image):
                raise ValueError("Input to predict() must be a PIL Image.")

            # Use self.transforms to preprocess (returns torch.Tensor)
            image_tensor = self.transforms(image_input).unsqueeze(0)  # Add batch dim

            # Run inference
            with torch.no_grad():
                outputs = self(image_tensor)
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
            raise  # Propagate the error instead of returning mock predictions

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
            "model_path": "",
            "device": str(""),
            "num_classes": len(self.class_names),
            "class_names": self.class_names,
            "model_type": "CustomNN" if self.is_loaded else "None",
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

    def preprocess_for_model(self, image_input) -> torch.Tensor:
        """
        Additional preprocessing specifically for the model
        Accepts PIL Image only
        """
        try:
            if not isinstance(image_input, Image.Image):
                raise ValueError("Input to preprocess_for_model() must be a PIL Image.")
            tensor = self.transforms(image_input)
            tensor = tensor.unsqueeze(0)  # Add batch dimension
            return tensor
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
