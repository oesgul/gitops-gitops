"""
Image Recognition Flask Application
Provides REST API endpoints for image classification and object detection.
"""

import os
import io
import logging
from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename

from image_processor import ImageProcessor
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize image processor
image_processor = ImageProcessor()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes."""
    return jsonify({
        'status': 'healthy',
        'service': 'image-recognition-app',
        'version': '1.0.0'
    }), 200

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint for Kubernetes probes."""
    try:
        # Test if the image processor is ready
        test_ready = image_processor.is_ready()
        if test_ready:
            return jsonify({
                'status': 'ready',
                'service': 'image-recognition-app'
            }), 200
        else:
            return jsonify({
                'status': 'not ready',
                'service': 'image-recognition-app'
            }), 503
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not ready',
            'error': str(e)
        }), 503

@app.route('/classify', methods=['POST'])
def classify_image():
    """
    Classify an uploaded image.
    
    Returns:
        JSON response with classification results
    """
    try:
        # Check if file is present in request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No image file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'File type not allowed. Supported types: png, jpg, jpeg, gif, bmp'
            }), 400
        
        # Process the image
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Perform classification
        results = image_processor.classify_image(image)
        
        return jsonify({
            'success': True,
            'filename': secure_filename(file.filename),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        return jsonify({
            'error': f'Classification failed: {str(e)}'
        }), 500

@app.route('/detect', methods=['POST'])
def detect_objects():
    """
    Detect objects in an uploaded image.
    
    Returns:
        JSON response with object detection results
    """
    try:
        # Check if file is present in request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No image file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'File type not allowed. Supported types: png, jpg, jpeg, gif, bmp'
            }), 400
        
        # Process the image
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Perform object detection
        results = image_processor.detect_objects(image)
        
        return jsonify({
            'success': True,
            'filename': secure_filename(file.filename),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Object detection error: {str(e)}")
        return jsonify({
            'error': f'Object detection failed: {str(e)}'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Perform comprehensive image analysis (classification + object detection).
    
    Returns:
        JSON response with complete analysis results
    """
    try:
        # Check if file is present in request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No image file selected'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'File type not allowed. Supported types: png, jpg, jpeg, gif, bmp'
            }), 400
        
        # Process the image
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Perform comprehensive analysis
        classification_results = image_processor.classify_image(image)
        detection_results = image_processor.detect_objects(image)
        
        return jsonify({
            'success': True,
            'filename': secure_filename(file.filename),
            'classification': classification_results,
            'object_detection': detection_results
        }), 200
        
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({
            'error': f'Image analysis failed: {str(e)}'
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Image Recognition API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'ready': '/ready',
            'classify': '/classify (POST)',
            'detect': '/detect (POST)',
            'analyze': '/analyze (POST)'
        },
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)