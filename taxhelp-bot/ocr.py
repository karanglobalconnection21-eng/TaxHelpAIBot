import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
from config import Config

pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH

class OCRProcessor:
    def __init__(self):
        pass

    def preprocess_image(self, image_bytes):
        """Preprocess image for better OCR results"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh

    def extract_text(self, image_bytes):
        """Extract text from image using OCR"""
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_bytes)

            # Convert back to PIL Image for pytesseract
            pil_image = Image.fromarray(processed_image)

            # Extract text
            text = pytesseract.image_to_string(pil_image, lang='eng')

            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_bytes):
        """Extract text from PDF (placeholder - would need pdf2image)"""
        # For now, return empty string - would implement PDF text extraction
        # using pdf2image + OCR for scanned PDFs
        return ""
