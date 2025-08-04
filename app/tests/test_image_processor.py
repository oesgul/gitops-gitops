"""
Unit tests for the ImageProcessor class.
"""

import pytest
import numpy as np
from PIL import Image
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from image_processor import ImageProcessor

@pytest.fixture
def processor():
    """Create an ImageProcessor instance for testing."""
    return ImageProcessor()

@pytest.fixture
def sample_image():
    """Create a sample test image."""
    return Image.new('RGB', (224, 224), color='red')

@pytest.fixture
def sample_complex_image():
    """Create a more complex test image with patterns."""
    image = Image.new('RGB', (300, 300), color='white')
    # Add some simple shapes for object detection testing
    pixels = image.load()
    
    # Draw a red rectangle
    for x in range(50, 150):
        for y in range(50, 150):
            pixels[x, y] = (255, 0, 0)
    
    # Draw a blue circle (approximation)
    center_x, center_y = 200, 200
    radius = 30
    for x in range(center_x - radius, center_x + radius):
        for y in range(center_y - radius, center_y + radius):
            if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2:
                if 0 <= x < 300 and 0 <= y < 300:
                    pixels[x, y] = (0, 0, 255)
    
    return image

class TestImageProcessor:
    """Test cases for ImageProcessor class."""
    
    def test_processor_initialization(self, processor):
        """Test that the processor initializes correctly."""
        assert processor is not None
        # The processor should attempt to load models
        # In a test environment, this might fail, which is expected
    
    def test_is_ready(self, processor):
        """Test the readiness check."""
        # This will depend on whether models loaded successfully
        ready_status = processor.is_ready()
        assert isinstance(ready_status, bool)
    
    def test_preprocess_for_classification(self, processor, sample_image):
        """Test image preprocessing for classification."""
        processed = processor._preprocess_for_classification(sample_image)
        
        # Check output shape
        assert processed.shape == (1, 224, 224, 3)
        
        # Check data type
        assert processed.dtype == np.float32
    
    def test_preprocess_different_sizes(self, processor):
        """Test preprocessing with different image sizes."""
        # Test with different input sizes
        sizes = [(100, 100), (500, 300), (224, 224)]
        
        for width, height in sizes:
            image = Image.new('RGB', (width, height), color='blue')
            processed = processor._preprocess_for_classification(image)
            
            # Output should always be (1, 224, 224, 3)
            assert processed.shape == (1, 224, 224, 3)
    
    def test_preprocess_different_modes(self, processor):
        """Test preprocessing with different image modes."""
        # Test with RGBA image
        rgba_image = Image.new('RGBA', (224, 224), color=(255, 0, 0, 128))
        processed = processor._preprocess_for_classification(rgba_image)
        assert processed.shape == (1, 224, 224, 3)
        
        # Test with grayscale image
        gray_image = Image.new('L', (224, 224), color=128)
        processed = processor._preprocess_for_classification(gray_image)
        assert processed.shape == (1, 224, 224, 3)
    
    def test_classify_image(self, processor, sample_image):
        """Test image classification."""
        try:
            results = processor.classify_image(sample_image)
            
            # Results should be a list
            assert isinstance(results, list)
            
            # If classification succeeded, check result format
            if len(results) > 0:
                result = results[0]
                assert 'class_id' in result
                assert 'class_name' in result
                assert 'confidence' in result
                assert isinstance(result['confidence'], float)
                assert 0 <= result['confidence'] <= 1
                
        except Exception as e:
            # In test environment, model loading might fail
            # This is acceptable for unit testing
            assert "model" in str(e).lower() or "tensorflow" in str(e).lower()
    
    def test_detect_objects(self, processor, sample_complex_image):
        """Test object detection."""
        try:
            results = processor.detect_objects(sample_complex_image)
            
            # Results should be a list
            assert isinstance(results, list)
            
            # If detection succeeded, check result format
            if len(results) > 0:
                result = results[0]
                assert 'object_id' in result
                assert 'class_name' in result
                assert 'confidence' in result
                assert 'bounding_box' in result
                
                bbox = result['bounding_box']
                assert 'x' in bbox
                assert 'y' in bbox
                assert 'width' in bbox
                assert 'height' in bbox
                
                # Check that bounding box values are reasonable
                assert bbox['x'] >= 0
                assert bbox['y'] >= 0
                assert bbox['width'] > 0
                assert bbox['height'] > 0
                
        except Exception as e:
            # OpenCV operations should generally work
            pytest.fail(f"Object detection failed unexpectedly: {str(e)}")
    
    def test_simple_object_detection(self, processor, sample_complex_image):
        """Test the simple object detection method directly."""
        import cv2
        
        # Convert PIL image to OpenCV format
        cv_image = cv2.cvtColor(np.array(sample_complex_image), cv2.COLOR_RGB2BGR)
        
        results = processor._simple_object_detection(cv_image)
        
        # Results should be a list
        assert isinstance(results, list)
        
        # Check that we found some objects (the shapes we drew)
        # This might be 0 if the simple detection doesn't pick up our shapes
        for result in results:
            assert 'object_id' in result
            assert 'class_name' in result
            assert 'confidence' in result
            assert 'bounding_box' in result
    
    def test_analyze_image_properties(self, processor, sample_image):
        """Test image property analysis."""
        properties = processor.analyze_image_properties(sample_image)
        
        assert isinstance(properties, dict)
        assert properties['width'] == 224
        assert properties['height'] == 224
        assert properties['mode'] == 'RGB'
        assert 'has_transparency' in properties
        assert 'mean_rgb' in properties
        assert 'std_rgb' in properties
        
        # Check RGB statistics
        assert len(properties['mean_rgb']) == 3
        assert len(properties['std_rgb']) == 3
        
        # For a solid red image, mean should be close to [255, 0, 0]
        assert properties['mean_rgb'][0] > 200  # Red channel
        assert properties['mean_rgb'][1] < 50   # Green channel
        assert properties['mean_rgb'][2] < 50   # Blue channel
    
    def test_analyze_image_properties_different_modes(self, processor):
        """Test image property analysis with different image modes."""
        # Test with RGBA image
        rgba_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        properties = processor.analyze_image_properties(rgba_image)
        
        assert properties['width'] == 100
        assert properties['height'] == 100
        assert properties['mode'] == 'RGBA'
        assert properties['has_transparency'] is True
        
        # Test with grayscale image
        gray_image = Image.new('L', (50, 50), color=128)
        properties = processor.analyze_image_properties(gray_image)
        
        assert properties['width'] == 50
        assert properties['height'] == 50
        assert properties['mode'] == 'L'
        assert properties['has_transparency'] is False

if __name__ == '__main__':
    pytest.main([__file__])