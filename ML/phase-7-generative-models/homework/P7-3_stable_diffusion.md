# Task P7-3: Hugging Face Diffusers (Stable Diffusion)

**Goal:** Use a state-of-the-art latent diffusion model to generate images, experiment with the guidance scale, and implement an image-to-image pipeline.

Create a Jupyter Notebook in `homework/lab-files/`. **Run on Google Colab (T4 GPU).**

## Part 1: Text-to-Image Generation
1. Install `diffusers`, `transformers`, and `accelerate`.
2. Load the Stable Diffusion pipeline (e.g., `runwayml/stable-diffusion-v1-5` or `stabilityai/stable-diffusion-xl-base-1.0` if you have enough RAM). Make sure to load it in `torch.float16` to save VRAM.
3. Generate an image from a prompt like `"A highly detailed oil painting of a futuristic city covered in snow, cinematic lighting"`.
4. Experiment with `num_inference_steps` (try 10, 20, 50). What happens to the quality and generation time?

## Part 2: Classifier-Free Guidance (CFG) Scale
The CFG scale (`guidance_scale`) controls how closely the image adheres to the text prompt.
1. Use the same seed and prompt, but generate a grid of 4 images with `guidance_scale` set to 1.0, 7.5, 15.0, and 30.0.
2. **Observation:** 
   - At 1.0, the model essentially ignores the prompt and generates a high-quality but random image.
   - At 7.5, you get a good balance of adherence and realism (this is the default).
   - At 30.0, the image usually looks deep-fried, over-saturated, and artistically ruined. The math forces the prompt conditioning too hard.

## Part 3: Image-to-Image (Img2Img)
Diffusion models can start from a *noisy* version of an existing image rather than pure random noise.
1. Load `AutoPipelineForImage2Image` (or `StableDiffusionImg2ImgPipeline`).
2. Download a basic sketch or a simple photo.
3. Pass the image to the pipeline with a descriptive prompt (e.g., `"A photorealistic highly detailed rendering"`).
4. Experiment with the `strength` parameter (0.0 to 1.0). 
   - `strength=0.2` will barely change the image (adds very little noise).
   - `strength=0.8` will completely change the image but keep the rough color blobs/composition.
