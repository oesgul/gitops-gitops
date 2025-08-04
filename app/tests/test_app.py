"""
Unit tests for the Flask application endpoints.
"""

import pytest
import io
import json
from PIL import Image
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_image():
    """Create a sample test image."""
    # Create a simple RGB image
    image = Image.new('RGB', (224, 224), color='red')
    img_io = io.BytesIO()
    image.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'image-recognition-app'
    assert 'version' in data

def test_readiness_endpoint(client):
    """Test the readiness check endpoint."""
    response = client.get('/ready')
    # Should return 200 if ready, 503 if not ready
    assert response.status_code in [200, 503]
    
    data = json.loads(response.data)
    assert 'status' in data
    assert data['service'] == 'image-recognition-app'

def test_index_endpoint(client):
    """Test the root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['service'] == 'Image Recognition API'
    assert 'endpoints' in data
    assert 'supported_formats' in data

def test_classify_no_file(client):
    """Test classification endpoint without file."""
    response = client.post('/classify')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No image file provided' in data['error']

def test_classify_empty_filename(client):
    """Test classification endpoint with empty filename."""
    response = client.post('/classify', data={'image': (io.BytesIO(), '')})
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No image file selected' in data['error']

def test_classify_invalid_file_type(client):
    """Test classification endpoint with invalid file type."""
    response = client.post('/classify', data={
        'image': (io.BytesIO(b'test'), 'test.txt')
    })
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'File type not allowed' in data['error']

def test_classify_valid_image(client, sample_image):
    """Test classification endpoint with valid image."""
    response = client.post('/classify', data={
        'image': (sample_image, 'test.jpg')
    })
    
    # Should return 200 if model is loaded, 500 if there's an error
    assert response.status_code in [200, 500]
    
    data = json.loads(response.data)
    if response.status_code == 200:
        assert data['success'] is True
        assert 'results' in data
        assert 'filename' in data
    else:
        assert 'error' in data

def test_detect_no_file(client):
    """Test object detection endpoint without file."""
    response = client.post('/detect')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No image file provided' in data['error']

def test_detect_valid_image(client, sample_image):
    """Test object detection endpoint with valid image."""
    response = client.post('/detect', data={
        'image': (sample_image, 'test.jpg')
    })
    
    # Should return 200 if processing succeeds, 500 if there's an error
    assert response.status_code in [200, 500]
    
    data = json.loads(response.data)
    if response.status_code == 200:
        assert data['success'] is True
        assert 'results' in data
        assert 'filename' in data
    else:
        assert 'error' in data

def test_analyze_no_file(client):
    """Test analysis endpoint without file."""
    response = client.post('/analyze')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No image file provided' in data['error']

def test_analyze_valid_image(client, sample_image):
    """Test analysis endpoint with valid image."""
    response = client.post('/analyze', data={
        'image': (sample_image, 'test.jpg')
    })
    
    # Should return 200 if processing succeeds, 500 if there's an error
    assert response.status_code in [200, 500]
    
    data = json.loads(response.data)
    if response.status_code == 200:
        assert data['success'] is True
        assert 'classification' in data
        assert 'object_detection' in data
        assert 'filename' in data
    else:
        assert 'error' in data

def test_allowed_file_extensions():
    """Test file extension validation."""
    from app import allowed_file
    
    # Valid extensions
    assert allowed_file('test.jpg') is True
    assert allowed_file('test.jpeg') is True
    assert allowed_file('test.png') is True
    assert allowed_file('test.gif') is True
    assert allowed_file('test.bmp') is True
    
    # Invalid extensions
    assert allowed_file('test.txt') is False
    assert allowed_file('test.pdf') is False
    assert allowed_file('test') is False
    assert allowed_file('') is False

if __name__ == '__main__':
    pytest.main([__file__])