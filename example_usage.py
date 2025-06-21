#!/usr/bin/env python3
"""
Example usage script for the Minimalist Anime Style Converter
This script demonstrates how to use the converter programmatically
"""

from main import MinimalistAnimeConverter
import os
from pathlib import Path

def example_basic_conversion():
    """Basic conversion example"""
    print("=== Basic Conversion Example ===")
    
    # Initialize converter
    converter = MinimalistAnimeConverter()
    
    # Example input path (you need to place an image here)
    input_path = "input/sample_image.jpg"
    
    if not os.path.exists(input_path):
        print(f"Please place a sample image at {input_path}")
        return
    
    # Convert with default settings
    output_path = converter.convert_image(input_path)
    print(f"Conversion completed! Output saved to: {output_path}")

def example_custom_settings():
    """Example with custom settings"""
    print("\n=== Custom Settings Example ===")
    
    converter = MinimalistAnimeConverter()
    
    input_path = "input/sample_image.jpg"
    if not os.path.exists(input_path):
        print(f"Please place a sample image at {input_path}")
        return
    
    # Convert with custom settings
    output_path = converter.convert_image(
        input_image_path=input_path,
        output_path="output/custom_result.jpg",
        strength=0.8,  # Stronger transformation
        guidance_scale=10.0,  # Higher guidance
        num_inference_steps=30  # More steps for better quality
    )
    print(f"Custom conversion completed! Output saved to: {output_path}")

def example_batch_processing():
    """Example of batch processing multiple images"""
    print("\n=== Batch Processing Example ===")
    
    converter = MinimalistAnimeConverter()
    
    input_dir = Path("input")
    output_dir = Path("output")
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    # Find all images in input directory
    image_files = [f for f in input_dir.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not image_files:
        print("No images found in input directory")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    for i, image_file in enumerate(image_files, 1):
        print(f"\nProcessing {i}/{len(image_files)}: {image_file.name}")
        
        output_path = output_dir / f"{image_file.stem}_minimalist{image_file.suffix}"
        
        try:
            converter.convert_image(
                input_image_path=str(image_file),
                output_path=str(output_path),
                strength=0.75,
                guidance_scale=7.5,
                num_inference_steps=20
            )
            print(f"✅ Completed: {output_path}")
        except Exception as e:
            print(f"❌ Error processing {image_file.name}: {str(e)}")

def main():
    """Main function to run examples"""
    print("Minimalist Anime Style Converter - Example Usage")
    print("=" * 50)
    
    # Create directories if they don't exist
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Run examples
    try:
        example_basic_conversion()
        example_custom_settings()
        example_batch_processing()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
