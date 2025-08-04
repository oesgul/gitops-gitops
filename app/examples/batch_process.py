#!/usr/bin/env python3
"""
Example script for batch processing multiple images through the API.
"""

import requests
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

def process_single_image(api_url, image_path, endpoint="analyze"):
    """Process a single image through the API."""
    try:
        with open(image_path, 'rb') as f:
            files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(f"{api_url}/{endpoint}", files=files, timeout=60)
        
        if response.status_code == 200:
            return {
                'image': image_path,
                'success': True,
                'data': response.json()
            }
        else:
            return {
                'image': image_path,
                'success': False,
                'error': response.json().get('error', 'Unknown error'),
                'status_code': response.status_code
            }
    except Exception as e:
        return {
            'image': image_path,
            'success': False,
            'error': str(e)
        }

def batch_process_images(api_url, image_directory, endpoint="analyze", max_workers=4, output_file=None):
    """Process multiple images in batch."""
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = []
    
    for root, dirs, files in os.walk(image_directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, file))
    
    if not image_files:
        print(f"No image files found in {image_directory}")
        return
    
    print(f"Found {len(image_files)} image files")
    print(f"Processing with {max_workers} workers...")
    
    results = []
    start_time = time.time()
    
    # Process images concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_image = {
            executor.submit(process_single_image, api_url, image_path, endpoint): image_path
            for image_path in image_files
        }
        
        # Collect results as they complete
        for i, future in enumerate(as_completed(future_to_image), 1):
            image_path = future_to_image[future]
            try:
                result = future.result()
                results.append(result)
                
                status = "✓" if result['success'] else "✗"
                print(f"[{i:3d}/{len(image_files)}] {status} {os.path.basename(image_path)}")
                
                if not result['success']:
                    print(f"    Error: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"[{i:3d}/{len(image_files)}] ✗ {os.path.basename(image_path)} - Exception: {e}")
                results.append({
                    'image': image_path,
                    'success': False,
                    'error': str(e)
                })
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\nProcessing completed in {processing_time:.2f} seconds")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Average time per image: {processing_time/len(results):.2f} seconds")
    
    # Save results to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    
    return results

def generate_summary_report(results, output_file="summary_report.txt"):
    """Generate a summary report from batch processing results."""
    successful_results = [r for r in results if r['success']]
    
    if not successful_results:
        print("No successful results to analyze")
        return
    
    # Analyze classification results
    class_counts = {}
    confidence_scores = []
    
    for result in successful_results:
        data = result['data']
        
        # Extract classification results
        if 'classification' in data:
            classifications = data['classification']
        elif 'results' in data:
            classifications = data['results']
        else:
            continue
        
        if classifications:
            top_class = classifications[0]
            class_name = top_class['class_name']
            confidence = top_class['confidence']
            
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            confidence_scores.append(confidence)
    
    # Generate report
    with open(output_file, 'w') as f:
        f.write("Image Recognition Batch Processing Summary\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total Images Processed: {len(results)}\n")
        f.write(f"Successful: {len(successful_results)}\n")
        f.write(f"Failed: {len(results) - len(successful_results)}\n\n")
        
        if confidence_scores:
            f.write(f"Average Confidence: {sum(confidence_scores)/len(confidence_scores):.3f}\n")
            f.write(f"Min Confidence: {min(confidence_scores):.3f}\n")
            f.write(f"Max Confidence: {max(confidence_scores):.3f}\n\n")
        
        f.write("Top Detected Classes:\n")
        f.write("-" * 30 + "\n")
        
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        for class_name, count in sorted_classes[:10]:
            f.write(f"{class_name:<25} {count:>4}\n")
        
        f.write("\nFailed Images:\n")
        f.write("-" * 30 + "\n")
        
        failed_results = [r for r in results if not r['success']]
        for result in failed_results:
            f.write(f"{os.path.basename(result['image'])}: {result.get('error', 'Unknown error')}\n")
    
    print(f"Summary report saved to {output_file}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Batch process images through the Image Recognition API')
    parser.add_argument('directory', help='Directory containing images to process')
    parser.add_argument('--api-url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--endpoint', choices=['classify', 'detect', 'analyze'], default='analyze',
                       help='API endpoint to use')
    parser.add_argument('--workers', type=int, default=4, help='Number of concurrent workers')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    parser.add_argument('--summary', help='Generate summary report file')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    print(f"Batch processing images from: {args.directory}")
    print(f"API URL: {args.api_url}")
    print(f"Endpoint: {args.endpoint}")
    print(f"Workers: {args.workers}")
    
    # Test API connectivity
    try:
        response = requests.get(f"{args.api_url}/health", timeout=10)
        if response.status_code != 200:
            print(f"Warning: API health check failed (status: {response.status_code})")
    except Exception as e:
        print(f"Error: Cannot connect to API at {args.api_url}: {e}")
        sys.exit(1)
    
    # Process images
    results = batch_process_images(
        args.api_url,
        args.directory,
        args.endpoint,
        args.workers,
        args.output
    )
    
    # Generate summary report if requested
    if args.summary:
        generate_summary_report(results, args.summary)

if __name__ == "__main__":
    main()