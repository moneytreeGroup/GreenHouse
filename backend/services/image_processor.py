from PIL import Image, ImageOps, ExifTags
import io
import numpy as np
from typing import Tuple, Dict, Any, Optional
import logging


class ImageProcessor:
    """Service for processing and validating images for plant identification"""

    def __init__(self):
        """Initialize image processor with default settings"""
        self.target_size = (224, 224)  # Standard size for most plant recognition models
        self.supported_formats = {"JPEG", "PNG", "WEBP", "JPG"}
        self.max_file_size = 16 * 1024 * 1024  # 16MB

    def is_valid_image(self, file) -> bool:
        """Check if uploaded file is a valid image"""
        try:
            # Check file extension
            if hasattr(file, "filename") and file.filename:
                ext = file.filename.lower().split(".")[-1]
                if ext not in ["jpg", "jpeg", "png", "webp"]:
                    return False

            # Try to open and verify the image
            file.seek(0)
            with Image.open(file) as img:
                img.verify()  # Verify it's a valid image
            file.seek(0)  # Reset file pointer
            return True

        except Exception as e:
            logging.warning(f"Image validation failed: {str(e)}")
            return False

    def preprocess_image(self, file) -> np.ndarray:
        """
        Preprocess image for model inference
        Returns: preprocessed image as numpy array
        """
        try:
            # Open and convert image
            file.seek(0)
            with Image.open(file) as img:
                # Handle EXIF orientation
                img = self._fix_orientation(img)

                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize image while maintaining aspect ratio
                img = self._resize_with_padding(img, self.target_size)

                # Convert to numpy array and normalize
                img_array = np.array(img, dtype=np.float32)
                img_array = img_array / 255.0  # Normalize to [0, 1]

                # Add batch dimension
                img_array = np.expand_dims(img_array, axis=0)

                return img_array

        except Exception as e:
            logging.error(f"Image preprocessing failed: {str(e)}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")

    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about an image file"""
        try:
            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "has_transparency": img.mode in ("RGBA", "LA", "P"),
                    "size_bytes": len(img.tobytes()),
                }
        except Exception as e:
            logging.error(f"Failed to get image info: {str(e)}")
            raise ValueError(f"Invalid image file: {str(e)}")

    def validate_image_stream(self, file) -> Dict[str, Any]:
        """Validate image from file stream and return info"""
        try:
            file.seek(0)
            with Image.open(file) as img:
                # Verify the image
                img.verify()

                # Re-open to get info (verify() closes the image)
                file.seek(0)
                with Image.open(file) as img:
                    return {
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode,
                        "has_transparency": img.mode in ("RGBA", "LA", "P"),
                    }
        except Exception as e:
            logging.error(f"Image stream validation failed: {str(e)}")
            raise ValueError(f"Invalid image: {str(e)}")

    def _fix_orientation(self, img: Image.Image) -> Image.Image:
        """Fix image orientation based on EXIF data"""
        try:
            # Check for EXIF orientation tag
            if hasattr(img, "_getexif"):
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == "Orientation":
                            if value == 3:
                                img = img.rotate(180, expand=True)
                            elif value == 6:
                                img = img.rotate(270, expand=True)
                            elif value == 8:
                                img = img.rotate(90, expand=True)
                            break
        except Exception as e:
            logging.warning(f"Could not fix image orientation: {str(e)}")

        return img

    def _resize_with_padding(
        self, img: Image.Image, target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Resize image to target size while maintaining aspect ratio using padding
        """
        # Calculate aspect ratios
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            # Image is wider - fit to width
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            # Image is taller - fit to height
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)

        # Resize image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Create new image with target size and paste resized image
        new_img = Image.new("RGB", target_size, (0, 0, 0))  # Black background

        # Calculate position to center the image
        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2

        new_img.paste(img, (x_offset, y_offset))

        return new_img

    def create_thumbnail(self, file, size: Tuple[int, int] = (150, 150)) -> bytes:
        """Create a thumbnail of the image"""
        try:
            file.seek(0)
            with Image.open(file) as img:
                # Fix orientation
                img = self._fix_orientation(img)

                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Save to bytes
                thumb_io = io.BytesIO()
                img.save(thumb_io, format="JPEG", quality=85)
                thumb_io.seek(0)

                return thumb_io.getvalue()

        except Exception as e:
            logging.error(f"Thumbnail creation failed: {str(e)}")
            raise ValueError(f"Failed to create thumbnail: {str(e)}")

    def enhance_image(self, img_array: np.ndarray) -> np.ndarray:
        """
        Apply image enhancements that might improve model accuracy
        """
        try:
            # Convert back to PIL for enhancement
            if img_array.ndim == 4:  # Remove batch dimension
                img_array = img_array[0]

            # Denormalize for PIL
            img_array = (img_array * 255).astype(np.uint8)
            img = Image.fromarray(img_array)

            # Apply subtle enhancements
            img = ImageOps.autocontrast(img, cutoff=1)  # Improve contrast
            img = ImageOps.equalize(img)  # Histogram equalization

            # Convert back to normalized numpy array
            enhanced_array = np.array(img, dtype=np.float32) / 255.0
            enhanced_array = np.expand_dims(
                enhanced_array, axis=0
            )  # Add batch dimension

            return enhanced_array

        except Exception as e:
            logging.warning(f"Image enhancement failed: {str(e)}")
            return img_array  # Return original if enhancement fails

    def validate_for_plant_recognition(self, file) -> Dict[str, Any]:
        """
        Specialized validation for plant recognition
        Returns validation result with recommendations
        """
        try:
            file.seek(0)
            with Image.open(file) as img:
                result = {
                    "valid": True,
                    "warnings": [],
                    "recommendations": [],
                    "image_info": {
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode,
                    },
                }

                # Check resolution
                if img.width < 200 or img.height < 200:
                    result["warnings"].append("Image resolution is quite low")
                    result["recommendations"].append(
                        "Use a higher resolution image for better accuracy"
                    )

                # Check aspect ratio
                aspect_ratio = img.width / img.height
                if aspect_ratio > 3 or aspect_ratio < 0.33:
                    result["warnings"].append("Unusual aspect ratio detected")
                    result["recommendations"].append(
                        "Square or rectangular images work best"
                    )

                # Check if image is too dark or bright
                img_array = np.array(img.convert("RGB"))
                mean_brightness = np.mean(img_array)

                if mean_brightness < 50:
                    result["warnings"].append("Image appears quite dark")
                    result["recommendations"].append(
                        "Try using a brighter image or improve lighting"
                    )
                elif mean_brightness > 200:
                    result["warnings"].append("Image appears overexposed")
                    result["recommendations"].append(
                        "Try using an image with less brightness"
                    )

                return result

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "warnings": ["Failed to analyze image"],
                "recommendations": ["Please try a different image file"],
            }
