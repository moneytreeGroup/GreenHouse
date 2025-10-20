import json
import os
from typing import List, Dict, Optional


class PlantCareService:
    """Service for managing plant care data from scraped information"""

    def __init__(self, data_file_path: str = None):
        """Initialize with path to plant care data JSON file"""
        if data_file_path is None:
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            backend_folder = os.path.dirname(backend_dir)
            data_file_path = os.path.join(backend_folder, "plant_care_data.json")

        self.data_file_path = data_file_path
        self.plant_data = self._load_plant_data()

    def _load_plant_data(self) -> List[Dict]:
        """Load plant care data from JSON file"""
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                print(f"Warning: Plant data file not found at {self.data_file_path}")
                return []
        except Exception as e:
            print(f"Error loading plant data: {e}")
            return []

    def get_care_data(self, plant_name: str) -> Optional[Dict]:
        """Get care data for a specific plant by name"""
        plant_name_lower = plant_name.lower().strip()
        print(os.path.exists(self.data_file_path), self.data_file_path)

        for plant in self.plant_data:
            if plant.get("name", "").lower() == plant_name_lower:
                return plant
        for plant in self.plant_data:
            stored_name = plant.get("name", "").lower()
            if (
                plant_name_lower in stored_name
                or stored_name in plant_name_lower
                or self._name_similarity(plant_name_lower, stored_name) > 0.8
            ):
                return plant

        return None
