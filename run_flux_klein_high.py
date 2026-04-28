import torch
from diffusers import Flux2Pipeline
from pathlib import Path
import time

OUTPUT_DIR = Path.cwd() / "flux_output"
OUTPUT_DIR.mkdir(exist_ok=True)

if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available. Re-check your PyTorch CUDA install.")

print("CUDA:", torch.cuda.get_device_name(0))

model_id = "black-forest-labs/FLUX.2-dev"
dtype = torch.bfloat16

print(f"⏳ Loading {model_id}...")

pipe = Flux2Pipeline.from_pretrained(
    model_id,
    torch_dtype=dtype,
)

# Best practical option for 12GB VRAM
pipe.enable_model_cpu_offload()

if hasattr(pipe, "enable_vae_tiling"):
    pipe.enable_vae_tiling()

if hasattr(pipe, "enable_vae_slicing"):
    pipe.enable_vae_slicing()

torch.cuda.empty_cache()

prompt = """
A highly detailed cinematic shot of a misty mountain village at golden hour,
volumetric light, intricate architecture, realistic atmosphere, sharp detail,
beautiful composition, professional digital painting
"""

height = 1024
width = 1024
steps = 40
guidance = 3.5
seed = 42

print(f"🎨 Generating {width}x{height}, {steps} steps, guidance {guidance}...")
start = time.time()

generator = torch.Generator(device="cuda").manual_seed(seed)

with torch.inference_mode():
    image = pipe(
        prompt=prompt,
        height=height,
        width=width,
        num_inference_steps=steps,
        guidance_scale=guidance,
        generator=generator,
    ).images[0]

elapsed = time.time() - start
output_path = OUTPUT_DIR / f"flux2_dev_seed{seed}_{int(elapsed)}s.png"
image.save(output_path)

print(f"✅ Done in {elapsed:.1f}s")
print(f"📁 Saved to: {output_path.resolve()}")