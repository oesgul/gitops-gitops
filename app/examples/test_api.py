#!/usr/bin/env python3
"""
Example script to test the Image Recognition API endpoints.
"""

import requests
import json
import sys
import os
from PIL import Image
import io

def create_test_image(filename="test_image.jpg", size=(224, 224), color="blue"):
    """Create a test image for API testing."""
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "purple": (128, 0, 128)
    }
    
    image = Image.new('RGB', size, colors.get(color, (0, 0, 255)))
    image.save(filename)
    return filename

def test_health_endpoint(base_url):
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_readiness_endpoint(base_url):
    """Test the readiness check endpoint."""
    print("\nTesting readiness endpoint...")
    try:
        response = requests.get(f"{base_url}/ready", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_info_endpoint(base_url):
    """Test the info endpoint."""
    print("\nTesting info endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_classify_endpoint(base_url, image_path):
    """Test the image classification endpoint."""
    print(f"\nTesting classification endpoint with {image_path}...")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (image_path, f, 'image/jpeg')}
            response = requests.post(f"{base_url}/classify", files=files, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_detect_endpoint(base_url, image_path):
    """Test the object detection endpoint."""
    print(f"\nTesting object detection endpoint with {image_path}...")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (image_path, f, 'image/jpeg')}
            response = requests.post(f"{base_url}/detect", files=files, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_analyze_endpoint(base_url, image_path):
    """Test the comprehensive analysis endpoint."""
    print(f"\nTesting analysis endpoint with {image_path}...")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (image_path, f, 'image/jpeg')}
            response = requests.post(f"{base_url}/analyze", files=files, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_file_type(base_url):
    """Test handling of invalid file types."""
    print("\nTesting invalid file type handling...")
    try:
        # Create a text file
        text_content = b"This is not an image file"
        files = {'image': ('test.txt', io.BytesIO(text_content), 'text/plain')}
        response = requests.post(f"{base_url}/classify", files=files, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_no_file(base_url):
    """Test handling when no file is provided."""
    print("\nTesting no file handling...")
    try:
        response = requests.post(f"{base_url}/classify", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 400
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function to run all tests."""
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"Testing Image Recognition API at: {base_url}")
    print("=" * 60)
    
    # Create test images
    test_images = []
    colors = ["red", "green", "blue", "yellow"]
    
    for i, color in enumerate(colors):
        filename = f"test_image_{color}.jpg"
        create_test_image(filename, color=color)
        test_images.append(filename)
        print(f"Created test image: {filename}")
    
    print("\n" + "=" * 60)
    
    # Run tests
    tests = [
        ("Health Check", lambda: test_health_endpoint(base_url)),
        ("Readiness Check", lambda: test_readiness_endpoint(base_url)),
        ("API Info", lambda: test_info_endpoint(base_url)),
        ("No File Error", lambda: test_no_file(base_url)),
        ("Invalid File Type", lambda: test_invalid_file_type(base_url)),
    ]
    
    # Add image processing tests for each test image
    for image_path in test_images:
        tests.extend([
            (f"Classification ({image_path})", lambda img=image_path: test_classify_endpoint(base_url, img)),
            (f"Object Detection ({image_path})", lambda img=image_path: test_detect_endpoint(base_url, img)),
            (f"Analysis ({image_path})", lambda img=image_path: test_analyze_endpoint(base_url, img)),
        ])
    
    # Execute tests
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    # Cleanup test images
    for image_path in test_images:
        try:
            os.remove(image_path)
        except:
            pass
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()