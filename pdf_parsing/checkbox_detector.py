import cv2
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

class CheckboxDetector:
    def __init__(self):
        # Configure default parameters
        self.aspect_ratio_range = (0.85, 1.15)
        self.size_range = (15, 25)
        self.solidity_threshold = 0.85
        self.edge_uniformity_threshold = 0.2
        self.black_pixel_ratio_threshold = 0.7

    def detect_checkboxes(self, image_array):
        """
        Detect checkboxes in an image.

        Args:
            image_array: Input image as numpy array

        Returns:
            list: List of detected checkboxes with their properties
        """
        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array

        # Apply adaptive thresholding with modified parameters
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Additional processing to remove small noise
        kernel = np.ones((2,2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        logging.info(f"Found {len(contours)} initial contours")

        checkboxes = []

        for i, contour in enumerate(contours):
            result = self._analyze_contour(contour, gray, thresh, i)
            if result and result.get('is_checkbox'):
                checkboxes.append(result)

        logging.info(f"Detected {len(checkboxes)} checkboxes")

        return checkboxes

    def _analyze_contour(self, contour, gray_image, thresh_image, index):
        """Analyze a single contour to determine if it's a checkbox."""
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

        if len(approx) != 4:
            return {'reason': 'not_quadrilateral', 'position': None}

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w)/h

        # Check basic size and ratio constraints
        if not (self.aspect_ratio_range[0] <= aspect_ratio <= self.aspect_ratio_range[1] and
                self.size_range[0] <= w <= self.size_range[1] and 
                self.size_range[0] <= h <= self.size_range[1]):
            return {
                'reason': 'size_ratio',
                'aspect_ratio': aspect_ratio,
                'size': (w, h),
                'position': (x, y, w, h)
            }

        # Analyze shape characteristics
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        contour_area = cv2.contourArea(contour)
        solidity = float(contour_area)/hull_area if hull_area > 0 else 0

        # Check edge uniformity
        edge_mask = np.zeros(thresh_image.shape, dtype=np.uint8)
        cv2.drawContours(edge_mask, [contour], 0, 255, 1)
        edge_pixels = cv2.countNonZero(edge_mask)
        expected_perimeter = 4 * w
        edge_uniformity = abs(edge_pixels - expected_perimeter) / expected_perimeter

        # Analyze inner region
        pad = 2
        inner_roi = gray_image[y+pad:y+h-pad, x+pad:x+w-pad]
        if inner_roi.size == 0:
            return {'reason': 'roi_empty', 'position': (x, y, w, h)}

        mean_value = cv2.mean(inner_roi)[0]
        std_value = np.std(inner_roi)

        # Calculate black pixel ratio
        _, binary_roi = cv2.threshold(inner_roi, 127, 255, cv2.THRESH_BINARY)
        black_pixel_ratio = 1.0 - (cv2.countNonZero(binary_roi) / inner_roi.size)

        # Determine if it's a checkbox
        is_checkbox = (
            solidity < self.solidity_threshold and
            edge_uniformity < self.edge_uniformity_threshold and
            black_pixel_ratio < self.black_pixel_ratio_threshold
        )

        if not is_checkbox:
            return {
                'reason': 'letter',
                'solidity': solidity,
                'edge_uniformity': edge_uniformity,
                'black_pixel_ratio': black_pixel_ratio,
                'position': (x, y, w, h)
            }

        # Determine if checkbox is checked
        is_checked = (std_value > 30 and
                     0.2 < black_pixel_ratio < 0.6 and
                     mean_value < 200)

        return {
            'is_checkbox': True,
            'position': (x, y, w, h),
            'checked': is_checked,
            'confidence': float(std_value),
            'center': (x + w//2, y + h//2),
            'solidity': solidity,
            'edge_uniformity': edge_uniformity,
            'black_pixel_ratio': black_pixel_ratio
        }
