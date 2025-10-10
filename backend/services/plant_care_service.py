import json
import os
from typing import List, Dict, Optional
import re


class PlantCareService:
    """Service for managing plant care data from scraped information"""

    def __init__(self, data_file_path: str = None):
        """Initialize with path to plant care data JSON file"""
        if data_file_path is None:
            # Default to the scraped data file in the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            data_file_path = os.path.join(project_root, "plant_care_data.json")

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

        # First try exact match
        for plant in self.plant_data:
            if plant.get("name", "").lower() == plant_name_lower:
                return plant

        # Try partial match (useful for plant names with variations)
        for plant in self.plant_data:
            stored_name = plant.get("name", "").lower()
            if (
                plant_name_lower in stored_name
                or stored_name in plant_name_lower
                or self._name_similarity(plant_name_lower, stored_name) > 0.8
            ):
                return plant

        return None

    def search_plants(self, search_term: str) -> List[Dict]:
        """Search for plants by name or care keywords"""
        search_term_lower = search_term.lower().strip()
        results = []

        for plant in self.plant_data:
            plant_name = plant.get("name", "").lower()
            care_data = plant.get("care", {})

            # Search in plant name
            if search_term_lower in plant_name:
                results.append(
                    {
                        "name": plant.get("name"),
                        "match_type": "name",
                        "relevance_score": self._calculate_relevance(
                            search_term_lower, plant_name
                        ),
                    }
                )
                continue

            # Search in care instructions
            care_text = " ".join(str(value).lower() for value in care_data.values())
            if search_term_lower in care_text:
                results.append(
                    {
                        "name": plant.get("name"),
                        "match_type": "care_instructions",
                        "relevance_score": self._calculate_relevance(
                            search_term_lower, care_text
                        ),
                    }
                )

        # Sort by relevance score (higher is better)
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Remove duplicates and limit results
        seen_names = set()
        unique_results = []
        for result in results:
            if result["name"] not in seen_names:
                seen_names.add(result["name"])
                unique_results.append(result)

        return unique_results[:10]  # Return top 10 matches

    def get_all_plants(self) -> List[Dict]:
        """Get list of all available plants with basic info"""
        plants_list = []

        for plant in self.plant_data:
            plant_info = {
                "name": plant.get("name"),
                "has_care_data": bool(plant.get("care")),
                "care_categories": list(plant.get("care", {}).keys()),
                "url": plant.get("url"),
            }
            plants_list.append(plant_info)

        # Sort alphabetically by name
        plants_list.sort(key=lambda x: x["name"].lower())
        return plants_list

    def get_plants_by_care_type(self, care_type: str) -> List[Dict]:
        """Get plants that have specific care information"""
        care_type_lower = care_type.lower()
        matching_plants = []

        for plant in self.plant_data:
            care_data = plant.get("care", {})
            if care_type_lower in [key.lower() for key in care_data.keys()]:
                matching_plants.append(
                    {
                        "name": plant.get("name"),
                        "care_info": care_data.get(care_type_lower, ""),
                        "url": plant.get("url"),
                    }
                )

        return matching_plants

    def get_care_summary(self, plant_name: str) -> Optional[Dict]:
        """Get a summarized version of care data for quick display"""
        plant_data = self.get_care_data(plant_name)
        if not plant_data:
            return None

        care = plant_data.get("care", {})
        summary = {
            "name": plant_data.get("name"),
            "light": self._extract_key_info(care.get("light_requirements", "")),
            "water": self._extract_key_info(care.get("watering_needs", "")),
            "soil": self._extract_key_info(care.get("soil_preferences", "")),
            "temperature": self._extract_key_info(care.get("temperature_humidity", "")),
            "full_care": care,
        }

        return summary

    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two plant names"""
        # Simple similarity based on common words
        words1 = set(re.findall(r"\w+", name1.lower()))
        words2 = set(re.findall(r"\w+", name2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _calculate_relevance(self, search_term: str, text: str) -> float:
        """Calculate relevance score for search results"""
        # Count occurrences and factor in position
        count = text.count(search_term)
        position_score = 1.0 if text.startswith(search_term) else 0.5
        length_factor = len(search_term) / len(text) if text else 0

        return count * position_score * (1 + length_factor)

    def _extract_key_info(self, care_text: str) -> str:
        """Extract key information from care text for summary"""
        if not care_text:
            return "Information not available"

        # Take first sentence or first 100 characters
        sentences = care_text.split(".")
        if sentences and len(sentences[0]) > 0:
            return sentences[0].strip() + "."

        return care_text[:100] + "..." if len(care_text) > 100 else care_text

    def reload_data(self) -> bool:
        """Reload plant data from file (useful if data is updated)"""
        try:
            self.plant_data = self._load_plant_data()
            return True
        except Exception as e:
            print(f"Error reloading plant data: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get statistics about the plant care database"""
        total_plants = len(self.plant_data)
        plants_with_care = sum(1 for plant in self.plant_data if plant.get("care"))

        care_categories = {}
        for plant in self.plant_data:
            for category in plant.get("care", {}).keys():
                care_categories[category] = care_categories.get(category, 0) + 1

        return {
            "total_plants": total_plants,
            "plants_with_care_data": plants_with_care,
            "care_categories": care_categories,
            "data_file_path": self.data_file_path,
            "file_exists": os.path.exists(self.data_file_path),
        }
