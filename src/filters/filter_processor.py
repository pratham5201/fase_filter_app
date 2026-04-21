"""
Filter Analysis and Feature Extraction Module
Extracts facial features and color characteristics for filter creation
"""

import numpy as np
import cv2
from typing import Dict, Tuple
from scipy import stats


class FilterAnalyzer:
    def __init__(self):
        self.features = {}

    def analyze_face(self, face_image: np.ndarray) -> Dict:
        """
        Analyze facial features and characteristics
        Returns dictionary with skin tone, makeup characteristics, etc.
        """
        features = {}
        
        # Extract color characteristics
        features['skin_tone'] = self._extract_skin_tone(face_image)
        features['color_profile'] = self._extract_color_profile(face_image)
        features['lighting'] = self._extract_lighting_info(face_image)
        features['makeup_intensity'] = self._estimate_makeup_intensity(face_image)
        features['texture'] = self._extract_texture_features(face_image)
        
        return features

    def _extract_skin_tone(self, image: np.ndarray) -> Dict:
        """Extract dominant skin tone color"""
        # Convert to HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Get dominant color in center region (likely skin)
        h, w = image.shape[:2]
        center_region = hsv_image[h//4:3*h//4, w//4:3*w//4]
        
        # Calculate mean color
        mean_h = np.mean(center_region[:, :, 0])
        mean_s = np.mean(center_region[:, :, 1])
        mean_v = np.mean(center_region[:, :, 2])
        
        # Convert back to BGR for storage
        hsv_color = np.uint8([[[mean_h, mean_s, mean_v]]])
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        
        return {
            'hsv': (float(mean_h), float(mean_s), float(mean_v)),
            'bgr': tuple(int(c) for c in bgr_color)
        }

    def _extract_color_profile(self, image: np.ndarray) -> Dict:
        """Extract overall color distribution"""
        # Get LAB color space for better color analysis
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Calculate mean and std for each channel
        mean_l = np.mean(lab_image[:, :, 0])
        mean_a = np.mean(lab_image[:, :, 1])
        mean_b = np.mean(lab_image[:, :, 2])
        
        std_l = np.std(lab_image[:, :, 0])
        std_a = np.std(lab_image[:, :, 1])
        std_b = np.std(lab_image[:, :, 2])
        
        return {
            'L': {'mean': float(mean_l), 'std': float(std_l)},
            'a': {'mean': float(mean_a), 'std': float(std_a)},
            'b': {'mean': float(mean_b), 'std': float(std_b)}
        }

    def _extract_lighting_info(self, image: np.ndarray) -> Dict:
        """Extract lighting characteristics"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        return {
            'brightness': float(np.mean(gray)),
            'contrast': float(np.std(gray))
        }

    def _estimate_makeup_intensity(self, image: np.ndarray) -> Dict:
        """Estimate makeup intensity from color saturation"""
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = hsv_image[:, :, 1]
        
        return {
            'saturation_mean': float(np.mean(saturation)),
            'saturation_std': float(np.std(saturation))
        }

    def _extract_texture_features(self, image: np.ndarray) -> Dict:
        """Extract texture information using edge detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Laplacian edge detection
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_energy = np.sum(laplacian ** 2)
        
        return {
            'texture_energy': float(texture_energy),
            'smoothness': float(1.0 / (1.0 + texture_energy / 1000.0))
        }


class FilterProcessor:
    def __init__(self):
        self.analyzer = FilterAnalyzer()

    def create_filter_from_samples(self, face_images: list) -> Dict:
        """
        Create a filter by analyzing multiple face samples
        Returns averaged filter characteristics
        """
        all_features = []
        
        for img in face_images:
            features = self.analyzer.analyze_face(img)
            all_features.append(features)
        
        # Average features
        averaged_filter = self._average_features(all_features)
        return averaged_filter

    def _average_features(self, features_list: list) -> Dict:
        """Average multiple feature dictionaries"""
        avg_filter = {
            'skin_tone': {
                'hsv': self._average_tuple([f['skin_tone']['hsv'] for f in features_list]),
                'bgr': self._average_tuple([f['skin_tone']['bgr'] for f in features_list])
            },
            'lighting': {
                'brightness': float(np.mean([f['lighting']['brightness'] for f in features_list])),
                'contrast': float(np.mean([f['lighting']['contrast'] for f in features_list]))
            },
            'makeup_intensity': {
                'saturation_mean': float(np.mean([f['makeup_intensity']['saturation_mean'] for f in features_list])),
                'saturation_std': float(np.mean([f['makeup_intensity']['saturation_std'] for f in features_list]))
            },
            'texture': {
                'smoothness': float(np.mean([f['texture']['smoothness'] for f in features_list]))
            }
        }
        
        return avg_filter

    def _average_tuple(self, tuples: list) -> Tuple:
        """Average a list of tuples"""
        arr = np.array(tuples)
        return tuple(np.mean(arr, axis=0))

    def apply_filter(self, image: np.ndarray, filter_profile: Dict, intensity: float = 0.8) -> np.ndarray:
        """
        Apply a filter to an image
        intensity: 0.0 to 1.0, how strong to apply the filter
        """
        result = image.copy().astype(np.float32)
        
        # Apply skin tone adjustment
        skin_tone = filter_profile['skin_tone']['hsv']
        result = self._apply_skin_tone(result, skin_tone, intensity)
        
        # Apply lighting adjustment
        lighting = filter_profile['lighting']
        result = self._apply_lighting(result, lighting, intensity)
        
        # Apply makeup effect
        makeup = filter_profile['makeup_intensity']
        result = self._apply_makeup_effect(result, makeup, intensity)
        
        # Apply smoothing for texture
        smoothness = filter_profile['texture']['smoothness']
        result = self._apply_smoothing(result, smoothness, intensity)
        
        return np.clip(result, 0, 255).astype(np.uint8)

    def _apply_skin_tone(self, image: np.ndarray, target_hsv: Tuple, intensity: float) -> np.ndarray:
        """Apply subtle skin tone enhancement"""
        image_uint8 = np.clip(image, 0, 255).astype(np.uint8)
        
        # Create a subtle brightening effect without color shift
        # This provides a natural filter look
        result = image_uint8.astype(np.float32)
        
        # Subtle overall brightening
        result = result * (1 + intensity * 0.1)
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result.astype(np.float32)

    def _apply_lighting(self, image: np.ndarray, lighting: Dict, intensity: float) -> np.ndarray:
        """Apply lighting adjustments"""
        image_uint8 = np.clip(image, 0, 255).astype(np.uint8)
        gray = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        current_brightness = np.mean(gray)
        target_brightness = lighting['brightness']
        
        brightness_diff = (target_brightness - current_brightness) * intensity * 0.1
        
        result = image.copy()
        result = result + brightness_diff
        
        return result

    def _apply_makeup_effect(self, image: np.ndarray, makeup: Dict, intensity: float) -> np.ndarray:
        """Apply subtle makeup saturation effect"""
        image_uint8 = np.clip(image, 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(image_uint8, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Very subtle saturation increase (makeup effect)
        sat_factor = 1 + intensity * 0.15
        hsv[:, :, 1] = hsv[:, :, 1] * sat_factor
        
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result.astype(np.float32)

    def _apply_smoothing(self, image: np.ndarray, smoothness: float, intensity: float) -> np.ndarray:
        """Apply smoothing for makeup effect"""
        image_uint8 = np.clip(image, 0, 255).astype(np.uint8)
        
        if smoothness > 0.7 and intensity > 0.3:
            # Apply bilateral filter for smoothing skin
            kernel_size = int(9 + smoothness * 10)
            if kernel_size % 2 == 0:
                kernel_size += 1
            
            smoothed = cv2.bilateralFilter(image_uint8, kernel_size, 20, 20)
            result = cv2.addWeighted(image_uint8, 1 - intensity * 0.3, smoothed, intensity * 0.3, 0)
            return result.astype(np.float32)
        
        return image
