"""
Unit tests for configuration settings.
"""

import pytest
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, config

class TestConfig:
    """Test cases for configuration classes."""
    
    def test_base_config(self):
        """Test base configuration class."""
        # Test default values
        assert Config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024  # 16MB
        assert Config.UPLOAD_FOLDER == '/app/uploads'
        assert Config.IMAGE_SIZE == (224, 224)
        assert Config.CONFIDENCE_THRESHOLD == 0.5
        assert Config.MAX_DETECTIONS == 10
        assert Config.LOG_LEVEL == 'INFO'
        assert Config.BATCH_SIZE == 1
        assert Config.USE_GPU is False
    
    def test_development_config(self):
        """Test development configuration."""
        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.LOG_LEVEL == 'DEBUG'
        
        # Should inherit from base config
        assert DevelopmentConfig.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
        assert DevelopmentConfig.CONFIDENCE_THRESHOLD == 0.5
    
    def test_production_config(self):
        """Test production configuration."""
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.LOG_LEVEL == 'INFO'
        
        # Should inherit from base config
        assert ProductionConfig.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
        assert ProductionConfig.CONFIDENCE_THRESHOLD == 0.5
    
    def test_testing_config(self):
        """Test testing configuration."""
        assert TestingConfig.TESTING is True
        assert TestingConfig.DEBUG is True
        assert TestingConfig.LOG_LEVEL == 'DEBUG'
        
        # Should inherit from base config
        assert TestingConfig.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
        assert TestingConfig.CONFIDENCE_THRESHOLD == 0.5
    
    def test_config_mapping(self):
        """Test configuration mapping dictionary."""
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config
        assert 'default' in config
        
        assert config['development'] == DevelopmentConfig
        assert config['production'] == ProductionConfig
        assert config['testing'] == TestingConfig
        assert config['default'] == DevelopmentConfig
    
    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        # Set environment variables
        os.environ['MAX_CONTENT_LENGTH'] = '8388608'  # 8MB
        os.environ['CONFIDENCE_THRESHOLD'] = '0.7'
        os.environ['MAX_DETECTIONS'] = '5'
        os.environ['LOG_LEVEL'] = 'WARNING'
        os.environ['USE_GPU'] = 'true'
        os.environ['IMAGE_SIZE'] = '256,256'
        
        # Reload the config module to pick up environment variables
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        # Test that environment variables are used
        assert config_module.Config.MAX_CONTENT_LENGTH == 8388608
        assert config_module.Config.CONFIDENCE_THRESHOLD == 0.7
        assert config_module.Config.MAX_DETECTIONS == 5
        assert config_module.Config.LOG_LEVEL == 'WARNING'
        assert config_module.Config.USE_GPU is True
        assert config_module.Config.IMAGE_SIZE == (256, 256)
        
        # Clean up environment variables
        for var in ['MAX_CONTENT_LENGTH', 'CONFIDENCE_THRESHOLD', 'MAX_DETECTIONS', 
                   'LOG_LEVEL', 'USE_GPU', 'IMAGE_SIZE']:
            if var in os.environ:
                del os.environ[var]
    
    def test_image_size_parsing(self):
        """Test IMAGE_SIZE environment variable parsing."""
        # Test different formats
        test_cases = [
            ('224,224', (224, 224)),
            ('256,256', (256, 256)),
            ('299,299', (299, 299)),
        ]
        
        for env_value, expected in test_cases:
            os.environ['IMAGE_SIZE'] = env_value
            
            # Reload config
            import importlib
            import config as config_module
            importlib.reload(config_module)
            
            assert config_module.Config.IMAGE_SIZE == expected
            
            # Clean up
            del os.environ['IMAGE_SIZE']
    
    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        # Test USE_GPU parsing
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('', False),
            ('invalid', False),
        ]
        
        for env_value, expected in test_cases:
            os.environ['USE_GPU'] = env_value
            
            # Reload config
            import importlib
            import config as config_module
            importlib.reload(config_module)
            
            assert config_module.Config.USE_GPU == expected
            
            # Clean up
            del os.environ['USE_GPU']

if __name__ == '__main__':
    pytest.main([__file__])