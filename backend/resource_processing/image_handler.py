import os
from PIL import Image
from backend.resource_processing.ocr import ocr_image

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


def extract_image(
    image_path: str,
    resource_id: str | None = None,
    enable_ocr: bool = True,
) -> dict:
    """
    Process a standalone image file (diagram, chart, textbook page, screenshot).

    Validates format, inspects dimensions, and extracts text using OCR.

    Args:
        image_path (str): File path to the image.
        resource_id (str, optional): Unique resource ID.
        enable_ocr (bool): Whether to perform OCR extraction.

    Returns:
        dict: Standardized image resource dictionary containing:
            - resource_id: str | None
            - source_type: "image"
            - source_name: str
            - image_format: str
            - dimensions: tuple[int, int] (width, height)
            - text: str (OCR text or empty string)
            - has_text: bool
            - is_ocr: bool
    """
    if not isinstance(image_path, str) or not image_path.strip():
        raise ValueError("image_path must be a non-empty string.")

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension '{ext}'. Supported: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}"
        )

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        with Image.open(image_path) as img:
            img.load()  # Verify image can be decoded
            width, height = img.size
            img_format = img.format or ext.lstrip(".").upper()

            extracted_text = ""
            if enable_ocr:
                extracted_text = ocr_image(img).strip()

            has_text = bool(extracted_text)

            return {
                "resource_id": resource_id,
                "source_type": "image",
                "source_name": os.path.basename(image_path),
                "image_format": img_format,
                "dimensions": {"width": width, "height": height},
                "text": extracted_text,
                "has_text": has_text,
                "is_ocr": has_text,
            }
    except Exception as exc:
        raise ValueError(f"Corrupted or invalid image file '{image_path}': {str(exc)}") from exc
