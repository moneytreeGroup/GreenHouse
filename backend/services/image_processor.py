from PIL import Image, ExifTags
from typing import Dict, Tuple, Any
import logging


class ImageProcessor:
    """Service for processing and validating images for plant identification"""

    def __init__(self):
        """Initialize image processor with default settings"""
        self.target_size = (224, 224)
        self.supported_formats = {"JPEG", "PNG", "WEBP", "JPG"}
        self.max_file_size = 16 * 1024 * 1024

    def is_valid_image(self, file) -> bool:
        """Check if uploaded file is a valid image"""
        try:
            if hasattr(file, "filename") and file.filename:
                ext = file.filename.lower().split(".")[-1]
                if ext not in ["jpg", "jpeg", "png", "webp"]:
                    return False

            file.seek(0)
            with Image.open(file) as img:
                img.verify()
            file.seek(0)
            return True

        except Exception as e:
            logging.warning(f"Image validation failed: {str(e)}")
            return False

    def preprocess_image(self, file) -> Image.Image:
        """
        Preprocess image for model inference
        Returns: preprocessed PIL Image (resized, padded, RGB, correct orientation)
        """
        try:
            file.seek(0)
            with Image.open(file) as img:
                img = self._fix_orientation(img)

                if img.mode != "RGB":
                    img = img.convert("RGB")

                img = self._resize_with_padding(img, self.target_size)

                return img

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

    def _fix_orientation(self, img: Image.Image) -> Image.Image:
        """Fix image orientation based on EXIF data"""
        try:
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
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        new_img = Image.new("RGB", target_size, (0, 0, 0))

        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2

        new_img.paste(img, (x_offset, y_offset))

        return new_img
