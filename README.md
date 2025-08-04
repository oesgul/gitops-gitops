# Image Recognition Application

This repository contains a complete image recognition application built with Flask and TensorFlow, designed to run on Kubernetes/OpenShift platforms.

## Features

- **Image Classification**: Classify images using pre-trained MobileNetV2 model
- **Object Detection**: Detect objects in images using OpenCV-based detection
- **Comprehensive Analysis**: Combined classification and object detection
- **REST API**: Easy-to-use HTTP endpoints for all functionality
- **Kubernetes Native**: Designed for cloud-native deployment
- **Health Checks**: Built-in health and readiness probes
- **Comprehensive Testing**: Unit, integration, and end-to-end tests

## Architecture

```
├── app/                          # Application code
│   ├── src/                      # Source code
│   │   ├── app.py               # Flask application
│   │   ├── image_processor.py   # Image processing logic
│   │   └── config.py            # Configuration management
│   ├── tests/                   # Test suite
│   ├── k8s/                     # Kubernetes manifests
│   ├── Dockerfile               # Container definition
│   └── requirements.txt         # Python dependencies
├── config/                      # OpenShift configuration
└── Jenkinsfile-app             # CI/CD pipeline
```

## API Endpoints

### Health Checks
- `GET /health` - Health check endpoint
- `GET /ready` - Readiness check endpoint

### Image Processing
- `POST /classify` - Classify an uploaded image
- `POST /detect` - Detect objects in an uploaded image
- `POST /analyze` - Comprehensive analysis (classification + detection)

### Information
- `GET /` - API information and available endpoints

## Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   cd app
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python src/app.py
   ```

3. **Test the API**
   ```bash
   curl -X POST -F "image=@test_image.jpg" http://localhost:5000/classify
   ```

### Docker Deployment

1. **Build the Image**
   ```bash
   cd app
   docker build -t image-recognition-app:latest .
   ```

2. **Run the Container**
   ```bash
   docker run -p 5000:5000 image-recognition-app:latest
   ```

### Kubernetes Deployment

1. **Deploy the Application**
   ```bash
   kubectl apply -k config/
   ```

2. **Check Deployment Status**
   ```bash
   kubectl get pods -n image-recognition
   ```

3. **Access the Application**
   ```bash
   kubectl port-forward svc/image-recognition-service 8080:80 -n image-recognition
   ```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_CONTENT_LENGTH` | `16777216` | Max file size (16MB) |
| `CONFIDENCE_THRESHOLD` | `0.5` | Minimum confidence for results |
| `MAX_DETECTIONS` | `10` | Maximum objects to detect |
| `IMAGE_SIZE` | `224,224` | Input image size for models |
| `USE_GPU` | `false` | Enable GPU acceleration |

## Testing

### Run Unit Tests
```bash
cd app
python -m pytest tests/ -v
```

### Run with Coverage
```bash
cd app
python -m pytest tests/ -v --cov=src --cov-report=html
```

### Run Integration Tests
```bash
cd app
python -m pytest tests/test_integration.py -v
```

## API Usage Examples

### Image Classification
```bash
curl -X POST \
  -F "image=@your_image.jpg" \
  http://localhost:5000/classify
```

Response:
```json
{
  "success": true,
  "filename": "your_image.jpg",
  "results": [
    {
      "class_id": "n02123045",
      "class_name": "tabby",
      "confidence": 0.8234
    }
  ]
}
```

### Object Detection
```bash
curl -X POST \
  -F "image=@your_image.jpg" \
  http://localhost:5000/detect
```

Response:
```json
{
  "success": true,
  "filename": "your_image.jpg",
  "results": [
    {
      "object_id": 0,
      "class_name": "object",
      "confidence": 0.75,
      "bounding_box": {
        "x": 100,
        "y": 150,
        "width": 200,
        "height": 180
      }
    }
  ]
}
```

### Comprehensive Analysis
```bash
curl -X POST \
  -F "image=@your_image.jpg" \
  http://localhost:5000/analyze
```

## CI/CD Pipeline

The application includes a Jenkins pipeline (`Jenkinsfile-app`) that:

1. **Builds** the Docker image
2. **Runs** comprehensive tests
3. **Performs** security scanning
4. **Pushes** to container registry
5. **Deploys** to development environment
6. **Runs** integration tests
7. **Deploys** to production (with approval)

## Monitoring and Observability

### Health Checks
- **Liveness Probe**: `/health` endpoint
- **Readiness Probe**: `/ready` endpoint

### Logging
- Structured logging with configurable levels
- Request/response logging
- Error tracking and reporting

### Metrics
- Application performance metrics
- Resource usage monitoring
- Custom business metrics

## Security

### Container Security
- Non-root user execution
- Minimal base image
- Security scanning in CI/CD

### API Security
- File type validation
- File size limits
- Input sanitization
- Error handling without information disclosure

### Kubernetes Security
- Service account with minimal permissions
- Network policies (when configured)
- Pod security contexts

## Scaling and Performance

### Horizontal Scaling
- Stateless application design
- Multiple replica support
- Load balancing ready

### Performance Optimization
- Model caching
- Efficient image processing
- Resource limits and requests
- GPU support (configurable)

## Troubleshooting

### Common Issues

1. **Model Loading Failures**
   - Check internet connectivity for model downloads
   - Verify sufficient memory allocation
   - Check TensorFlow compatibility

2. **Image Processing Errors**
   - Validate image format and size
   - Check file upload limits
   - Verify OpenCV installation

3. **Deployment Issues**
   - Check resource quotas
   - Verify image pull policies
   - Review pod logs: `kubectl logs -f deployment/image-recognition-app -n image-recognition`

### Debug Commands
```bash
# Check pod status
kubectl get pods -n image-recognition

# View logs
kubectl logs -f deployment/image-recognition-app -n image-recognition

# Describe deployment
kubectl describe deployment image-recognition-app -n image-recognition

# Port forward for local testing
kubectl port-forward svc/image-recognition-service 8080:80 -n image-recognition
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation