import os
import argparse
import torch
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from PIL import Image
import requests
from pathlib import Path
import hashlib

class MinimalistAnimeConverter:
    def __init__(self, model_path="./models", device="auto"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        # Auto-detect device
        if device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
            
        print(f"Using device: {self.device}")
        
        # LoRA model info
        self.lora_url = "https://civitai.com/api/download/models/29709?type=Model&format=SafeTensor&size=full&fp=fp16"
        self.lora_filename = "minimalist_anime_style.safetensors"
        self.lora_hash = "F16F6504EF"
        
        self.pipeline = None
        
    def download_lora_model(self):
        """Download the LoRA model if it doesn't exist"""
        lora_path = self.model_path / self.lora_filename
        
        if lora_path.exists():
            # Verify hash
            with open(lora_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest().upper()[:10]
                if file_hash == self.lora_hash:
                    print("LoRA model already exists and verified.")
                    return str(lora_path)
                else:
                    print("LoRA model exists but hash mismatch. Re-downloading...")
        
        print("Downloading LoRA model...")
        response = requests.get(self.lora_url, stream=True)
        response.raise_for_status()
        
        with open(lora_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"LoRA model downloaded to {lora_path}")
        return str(lora_path)
    
    def setup_pipeline(self):
        """Setup the Stable Diffusion pipeline with LoRA"""
        print("Setting up Stable Diffusion pipeline...")
        
        # Load base model (SD 1.5)
        model_id = "runwayml/stable-diffusion-v1-5"
        
        self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        # Use DPM++ scheduler for better quality
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config
        )
        
        # Load LoRA weights
        lora_path = self.download_lora_model()
        try:
            # Try loading as LoRA adapter
            self.pipeline.load_lora_weights(lora_path, adapter_name="minimalist_anime")
            self.pipeline.set_adapters("minimalist_anime")
        except Exception as e:
            print(f"Warning: Could not load LoRA weights: {e}")
            print("Continuing without LoRA - results may differ from expected style")
        
        # Move to device
        self.pipeline = self.pipeline.to(self.device)
        
        # Enable memory efficient attention if available
        if hasattr(self.pipeline, "enable_attention_slicing"):
            self.pipeline.enable_attention_slicing()
        # Note: xformers removed due to installation issues
        # if hasattr(self.pipeline, "enable_xformers_memory_efficient_attention"):
        #     try:
        #         self.pipeline.enable_xformers_memory_efficient_attention()
        #     except:
        #         pass
        
        print("Pipeline setup complete!")
    
    def convert_image(self, input_image_path, output_path=None, strength=0.75, guidance_scale=7.5, num_inference_steps=20):
        """Convert an image to minimalist anime style"""
        if self.pipeline is None:
            self.setup_pipeline()
        
        # Load and preprocess input image
        input_image = Image.open(input_image_path).convert("RGB")
        
        # Resize image if too large (to save memory)
        max_size = 768
        if max(input_image.size) > max_size:
            ratio = max_size / max(input_image.size)
            new_size = (int(input_image.size[0] * ratio), int(input_image.size[1] * ratio))
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Generate prompt
        prompt = "anime minimalist, simple, clean lines, minimal colors, flat design"
        negative_prompt = "complex, detailed, busy, cluttered, realistic, photographic, 3d render"
        
        print(f"Converting image: {input_image_path}")
        print(f"Image size: {input_image.size}")
        print(f"Prompt: {prompt}")
        
        # Generate image
        with torch.autocast(self.device if self.device != "mps" else "cpu"):
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=input_image,
                strength=strength,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                generator=torch.Generator(device=self.device).manual_seed(42)
            )
        
        output_image = result.images[0]
        
        # Save output
        if output_path is None:
            input_path = Path(input_image_path)
            output_path = input_path.parent / f"{input_path.stem}_minimalist{input_path.suffix}"
        
        output_image.save(output_path)
        print(f"Converted image saved to: {output_path}")
        
        return output_path

def main():
    parser = argparse.ArgumentParser(description="Convert images to minimalist anime style")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output image path")
    parser.add_argument("-s", "--strength", type=float, default=0.75, 
                       help="Transformation strength (0.0-1.0, default: 0.75)")
    parser.add_argument("-g", "--guidance-scale", type=float, default=7.5,
                       help="Guidance scale (default: 7.5)")
    parser.add_argument("-n", "--num-steps", type=int, default=20,
                       help="Number of inference steps (default: 20)")
    parser.add_argument("-d", "--device", default="auto",
                       help="Device to use (auto, cuda, mps, cpu)")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.")
        return
    
    # Create converter and process image
    converter = MinimalistAnimeConverter(device=args.device)
    
    try:
        output_path = converter.convert_image(
            input_image_path=args.input,
            output_path=args.output,
            strength=args.strength,
            guidance_scale=args.guidance_scale,
            num_inference_steps=args.num_steps
        )
        print(f"\n✅ Conversion completed successfully!")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        return

if __name__ == "__main__":
    main()
