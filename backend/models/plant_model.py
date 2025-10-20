import torch
import torch.nn as nn
import torchvision.transforms as transforms
from typing import List, Dict
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
            num_classes = 19

        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        self.conv2 = nn.Conv2d(64, 96, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(96)
        self.drop2 = nn.Dropout2d(0.1)

        self.conv3 = nn.Conv2d(96, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.conv4 = nn.Conv2d(128, 192, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(192)
        self.drop4 = nn.Dropout2d(0.1)

        self.conv5 = nn.Conv2d(192, 256, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(256)

        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((6, 6))

        self.fc1 = nn.Linear(256 * 6 * 6, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)
        self.class_names = []
        self.is_loaded = False
        self.confidence_threshold = 0.5

        self.transforms = transforms.Compose(
            [
                transforms.Resize((150, 150)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

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
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.drop2(x)

        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        x = self.drop4(x)

        x = self.pool(F.relu(self.bn5(self.conv5(x))))

        x = self.adaptive_pool(x)

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

            if "class_names" in checkpoint:
                self.class_names = checkpoint["class_names"]
                self.plant_classes = checkpoint["class_names"]
        else:
            state_dict = checkpoint

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
            if not isinstance(image_input, Image.Image):
                raise ValueError("Input to predict() must be a PIL Image.")

            image_tensor = self.transforms(image_input).unsqueeze(0)

            with torch.no_grad():
                outputs = self(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)

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
            raise

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
