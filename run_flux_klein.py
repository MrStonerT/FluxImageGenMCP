import torch
from diffusers import Flux2KleinPipeline
from pathlib import Path
import time

# 🔧 Output config
OUTPUT_DIR = Path.cwd() / "flux_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 🖥️ Device & precision
if not torch.cuda.is_available():
    raise RuntimeError("CUDA is not available. Re-check your PyTorch CUDA install.")

device = "cuda"
dtype = torch.bfloat16  # RTX 4070 supports bf16

print("CUDA:", torch.cuda.get_device_name(0))
print("⏳ Loading FLUX.2-klein...")

pipe = Flux2KleinPipeline.from_pretrained(
    "black-forest-labs/FLUX.2-klein-4B",
    torch_dtype=dtype,
)

# 💡 VRAM optimizations for 12GB GPU
# Use ONE offload strategy. model_cpu_offload is usually better/faster than sequential.
pipe.enable_model_cpu_offload()

# Some pipelines support this, Flux2KleinPipeline may not.
if hasattr(pipe, "enable_vae_tiling"):
    pipe.enable_vae_tiling()

if hasattr(pipe, "enable_vae_slicing"):
    pipe.enable_vae_slicing()

# Optional memory cleanup
torch.cuda.empty_cache()

# 🎨 Prompt
prompt = "A highly detailed cinematic shot of a misty mountain village at golden hour, digital painting style"

steps = 28
guidance = 1.0
seed = 42
height = 1024
width = 1024

print(f"🎨 Generating {width}x{height}, {steps} steps...")
start = time.time()

generator = torch.Generator(device=device).manual_seed(seed)

with torch.inference_mode():
    image = pipe(
        prompt=prompt,
        height=height,
        width=width,
        guidance_scale=guidance,
        num_inference_steps=steps,
        generator=generator,
    ).images[0]

elapsed = time.time() - start
output_path = OUTPUT_DIR / f"flux_klein_seed{seed}_{int(elapsed)}s.png"
image.save(output_path)

print(f"✅ Done in {elapsed:.1f}s")
print(f"📁 Saved to: {output_path.resolve()}")