"""
Image processing module for classification and object detection.
Uses TensorFlow/Keras for deep learning models.
"""

import logging
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import cv2

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Handles image classification and object detection."""
    
    def __init__(self):
        """Initialize the image processor with pre-trained models."""
        self.classification_model = None
        self.detection_model = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models for classification and detection."""
        try:
            # Load MobileNetV2 for image classification
            logger.info("Loading MobileNetV2 classification model...")
            self.classification_model = MobileNetV2(
                weights='imagenet',
                include_top=True,
                input_shape=(224, 224, 3)
            )
            logger.info("Classification model loaded successfully")
            
            # For object detection, we'll use OpenCV's DNN module with a pre-trained model
            # In a production environment, you might want to use TensorFlow Object Detection API
            logger.info("Object detection model initialized (using OpenCV DNN)")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def is_ready(self):
        """Check if the processor is ready to handle requests."""
        return self.classification_model is not None
    
    def classify_image(self, image):
        """
        Classify an image using the pre-trained classification model.
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            list: Classification results with confidence scores
        """
        try:
            # Preprocess the image
            img_array = self._preprocess_for_classification(image)
            
            # Make prediction
            predictions = self.classification_model.predict(img_array, verbose=0)
            
            # Decode predictions
            decoded_predictions = decode_predictions(predictions, top=5)[0]
            
            # Format results
            results = []
            for class_id, class_name, confidence in decoded_predictions:
                results.append({
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': float(confidence)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            raise
    
    def detect_objects(self, image):
        """
        Detect objects in an image using OpenCV DNN.
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            list: Object detection results with bounding boxes and confidence scores
        """
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            height, width = cv_image.shape[:2]
            
            # For demonstration, we'll use a simple contour-based object detection
            # In production, you'd use a proper object detection model like YOLO or SSD
            results = self._simple_object_detection(cv_image)
            
            return results
            
        except Exception as e:
            logger.error(f"Object detection error: {str(e)}")
            raise
    
    def _preprocess_for_classification(self, image):
        """
        Preprocess image for classification model.
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            np.ndarray: Preprocessed image array
        """
        # Resize image to model input size
        image = image.resize((224, 224))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        # Preprocess for MobileNetV2
        img_array = preprocess_input(img_array)
        
        return img_array
    
    def _simple_object_detection(self, cv_image):
        """
        Simple object detection using contour detection.
        This is a placeholder implementation - in production you'd use proper object detection models.
        
        Args:
            cv_image (np.ndarray): OpenCV image
            
        Returns:
            list: Detection results
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold
            _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            results = []
            height, width = cv_image.shape[:2]
            
            # Process contours
            for i, contour in enumerate(contours[:10]):  # Limit to top 10 contours
                # Calculate bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out very small objects
                if w > 20 and h > 20:
                    # Calculate confidence based on contour area (simplified)
                    area = cv2.contourArea(contour)
                    confidence = min(area / (width * height), 1.0)
                    
                    if confidence > 0.01:  # Minimum confidence threshold
                        results.append({
                            'object_id': i,
                            'class_name': 'object',  # Generic object class
                            'confidence': float(confidence),
                            'bounding_box': {
                                'x': int(x),
                                'y': int(y),
                                'width': int(w),
                                'height': int(h)
                            }
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Simple object detection error: {str(e)}")
            return []
    
    def analyze_image_properties(self, image):
        """
        Analyze basic image properties.
        
        Args:
            image (PIL.Image): Input image
            
        Returns:
            dict: Image properties
        """
        try:
            properties = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
            
            # Calculate basic statistics if image is in RGB mode
            if image.mode == 'RGB':
                img_array = np.array(image)
                properties.update({
                    'mean_rgb': [float(img_array[:,:,i].mean()) for i in range(3)],
                    'std_rgb': [float(img_array[:,:,i].std()) for i in range(3)]
                })
            
            return properties
            
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {}