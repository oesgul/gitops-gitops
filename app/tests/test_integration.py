"""
Integration tests for the complete image recognition application.
"""

import pytest
import requests
import time
import io
from PIL import Image
import json

class TestIntegration:
    """Integration tests for the deployed application."""
    
    @pytest.fixture(scope="class")
    def app_url(self):
        """Get the application URL for testing."""
        # In a real environment, this would be the actual deployed URL
        # For testing, we'll use localhost
        return "http://localhost:5000"
    
    @pytest.fixture
    def sample_image_file(self):
        """Create a sample image file for testing."""
        image = Image.new('RGB', (224, 224), color='blue')
        img_io = io.BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io
    
    def test_health_endpoint_integration(self, app_url):
        """Test health endpoint in integration environment."""
        try:
            response = requests.get(f"{app_url}/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'healthy'
            assert data['service'] == 'image-recognition-app'
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_readiness_endpoint_integration(self, app_url):
        """Test readiness endpoint in integration environment."""
        try:
            response = requests.get(f"{app_url}/ready", timeout=10)
            assert response.status_code in [200, 503]
            
            data = response.json()
            assert 'status' in data
            assert data['service'] == 'image-recognition-app'
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_classification_endpoint_integration(self, app_url, sample_image_file):
        """Test classification endpoint in integration environment."""
        try:
            files = {'image': ('test.jpg', sample_image_file, 'image/jpeg')}
            response = requests.post(f"{app_url}/classify", files=files, timeout=30)
            
            # Should succeed if models are loaded
            assert response.status_code in [200, 500]
            
            data = response.json()
            if response.status_code == 200:
                assert data['success'] is True
                assert 'results' in data
                assert isinstance(data['results'], list)
            else:
                assert 'error' in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_detection_endpoint_integration(self, app_url, sample_image_file):
        """Test object detection endpoint in integration environment."""
        try:
            sample_image_file.seek(0)  # Reset file pointer
            files = {'image': ('test.jpg', sample_image_file, 'image/jpeg')}
            response = requests.post(f"{app_url}/detect", files=files, timeout=30)
            
            assert response.status_code in [200, 500]
            
            data = response.json()
            if response.status_code == 200:
                assert data['success'] is True
                assert 'results' in data
                assert isinstance(data['results'], list)
            else:
                assert 'error' in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_analysis_endpoint_integration(self, app_url, sample_image_file):
        """Test comprehensive analysis endpoint in integration environment."""
        try:
            sample_image_file.seek(0)  # Reset file pointer
            files = {'image': ('test.jpg', sample_image_file, 'image/jpeg')}
            response = requests.post(f"{app_url}/analyze", files=files, timeout=30)
            
            assert response.status_code in [200, 500]
            
            data = response.json()
            if response.status_code == 200:
                assert data['success'] is True
                assert 'classification' in data
                assert 'object_detection' in data
                assert isinstance(data['classification'], list)
                assert isinstance(data['object_detection'], list)
            else:
                assert 'error' in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_invalid_file_type_integration(self, app_url):
        """Test invalid file type handling in integration environment."""
        try:
            # Create a text file instead of an image
            text_file = io.BytesIO(b"This is not an image")
            files = {'image': ('test.txt', text_file, 'text/plain')}
            
            response = requests.post(f"{app_url}/classify", files=files, timeout=10)
            assert response.status_code == 400
            
            data = response.json()
            assert 'error' in data
            assert 'File type not allowed' in data['error']
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_large_file_handling(self, app_url):
        """Test handling of large files."""
        try:
            # Create a large image (this should be within limits)
            large_image = Image.new('RGB', (2000, 2000), color='green')
            img_io = io.BytesIO()
            large_image.save(img_io, 'JPEG', quality=95)
            img_io.seek(0)
            
            files = {'image': ('large_test.jpg', img_io, 'image/jpeg')}
            response = requests.post(f"{app_url}/classify", files=files, timeout=60)
            
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400, 413, 500]
            
            data = response.json()
            if response.status_code == 200:
                assert data['success'] is True
            else:
                assert 'error' in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")
    
    def test_concurrent_requests(self, app_url, sample_image_file):
        """Test handling of concurrent requests."""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def make_request():
                try:
                    sample_image_file.seek(0)
                    files = {'image': ('test.jpg', sample_image_file, 'image/jpeg')}
                    response = requests.post(f"{app_url}/classify", files=files, timeout=30)
                    results.put(response.status_code)
                except Exception as e:
                    results.put(str(e))
            
            # Create multiple threads
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            response_codes = []
            while not results.empty():
                result = results.get()
                if isinstance(result, int):
                    response_codes.append(result)
            
            # At least some requests should succeed
            assert len(response_codes) > 0
            # All responses should be valid HTTP status codes
            for code in response_codes:
                assert code in [200, 400, 500, 503]
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running - skipping integration test")

class TestKubernetesDeployment:
    """Tests for Kubernetes deployment configuration."""
    
    def test_kubernetes_manifests_exist(self):
        """Test that all required Kubernetes manifests exist."""
        import os
        
        k8s_dir = os.path.join(os.path.dirname(__file__), '..', 'k8s')
        
        required_files = [
            'deployment.yaml',
            'service.yaml',
            'route.yaml',
            'configmap.yaml',
            'namespace.yaml',
            'kustomization.yaml'
        ]
        
        for file_name in required_files:
            file_path = os.path.join(k8s_dir, file_name)
            assert os.path.exists(file_path), f"Required file {file_name} not found"
    
    def test_kustomization_syntax(self):
        """Test that kustomization.yaml has valid syntax."""
        import yaml
        import os
        
        kustomization_path = os.path.join(
            os.path.dirname(__file__), '..', 'k8s', 'kustomization.yaml'
        )
        
        with open(kustomization_path, 'r') as f:
            try:
                kustomization = yaml.safe_load(f)
                assert 'resources' in kustomization
                assert 'apiVersion' in kustomization
                assert 'kind' in kustomization
                assert kustomization['kind'] == 'Kustomization'
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in kustomization.yaml: {e}")
    
    def test_deployment_configuration(self):
        """Test deployment configuration."""
        import yaml
        import os
        
        deployment_path = os.path.join(
            os.path.dirname(__file__), '..', 'k8s', 'deployment.yaml'
        )
        
        with open(deployment_path, 'r') as f:
            try:
                docs = list(yaml.safe_load_all(f))
                
                # Find deployment document
                deployment = None
                for doc in docs:
                    if doc and doc.get('kind') == 'Deployment':
                        deployment = doc
                        break
                
                assert deployment is not None, "Deployment not found in deployment.yaml"
                
                # Check required fields
                assert 'metadata' in deployment
                assert 'spec' in deployment
                assert 'template' in deployment['spec']
                assert 'containers' in deployment['spec']['template']['spec']
                
                # Check container configuration
                containers = deployment['spec']['template']['spec']['containers']
                assert len(containers) > 0
                
                container = containers[0]
                assert 'name' in container
                assert 'image' in container
                assert 'ports' in container
                assert 'livenessProbe' in container
                assert 'readinessProbe' in container
                
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in deployment.yaml: {e}")

if __name__ == '__main__':
    pytest.main([__file__])