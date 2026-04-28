from __future__ import annotations

import argparse
import importlib.util
import inspect
import logging
import os
import re
import secrets
import statistics
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

HF_HOME_PATH = Path(r"B:\Pond\hf_cache")
OUTPUT_DIR = Path(r"B:\Pond\FluxImageGen\flux_output")

os.environ.setdefault("HF_HOME", str(HF_HOME_PATH))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import torch
from diffusers import (
    Flux2KleinPipeline,
    Flux2Pipeline,
    Flux2Transformer2DModel,
    GGUFQuantizationConfig,
)
from mcp.server.fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stderr,
    force=True,
)
LOGGER = logging.getLogger("flux-mcp")

MODE_LOW = "low"
MODE_HIGH = "high"
MODE_FAST = "fast"
RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}

mcp = FastMCP("FLUX Image Generator", json_response=True)


@dataclass(frozen=True)
class ModeConfig:
    mode: str
    model_id: str
    pipeline_cls: type[Any]
    default_width: int
    default_height: int
    default_steps: int
    default_guidance_scale: float
    dtype: torch.dtype = torch.bfloat16
    gguf_path: str | None = None
    gguf_config_repo: str | None = None


@dataclass
class Metrics:
    server_started_at: str
    selected_mode: str
    selected_model_id: str
    load_strategy: str
    server_transport: str
    cuda_available: bool
    cuda_version: str | None
    gpu_name: str
    total_vram_gb: float | None = None
    free_vram_at_start_gb: float | None = None
    process_id: int = 0
    is_generating: bool = False
    current_request_started_at: str | None = None
    total_images_generated: int = 0
    last_generation_seconds: float | None = None
    average_generation_seconds: float | None = None
    last_generated_at: str | None = None
    last_output_path: str | None = None
    generation_history: list[float] = field(default_factory=list)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_output_name(output_name: str | None, mode: str, seed: int) -> str:
    if output_name:
        candidate = Path(output_name).name
        stem = Path(candidate).stem
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = f"flux_{mode}_{timestamp}_seed{seed}"

    stem = re.sub(r"[^\w.-]+", "_", stem, flags=re.ASCII).strip(" ._")
    stem = re.sub(r"_+", "_", stem)

    if not stem:
        stem = f"flux_{mode}_seed{seed}"
    if stem.upper() in RESERVED_NAMES:
        stem = f"img_{stem}"

    stem = stem[:120]
    return f"{stem}.png"


def choose_high_resolution_defaults() -> tuple[int, int]:
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if total_vram_gb >= 16:
        return 1024, 1024
    return 768, 768


def choose_low_defaults() -> tuple[int, int, int, float]:
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if total_vram_gb >= 16:
        return 1024, 1024, 32, 1.5
    if total_vram_gb >= 12:
        return 704, 704, 16, 1.5
    return 640, 640, 12, 1.25


def choose_fast_defaults() -> tuple[int, int, int, float]:
    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if total_vram_gb >= 16:
        return 1024, 1024, 4, 1.0
    if total_vram_gb >= 12:
        return 768, 768, 4, 1.0
    return 640, 640, 4, 1.0


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return int(value)


def env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    return float(value)


def get_free_vram_gb() -> float | None:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.free",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        first_line = result.stdout.strip().splitlines()[0]
        return round(int(first_line) / 1024, 3)
    except Exception:
        pass

    try:
        free_bytes, _ = torch.cuda.mem_get_info()
    except Exception:
        return None
    return round(free_bytes / (1024**3), 3)


def get_mode_config(mode: str) -> ModeConfig:
    if mode == MODE_LOW:
        width, height, steps, guidance = choose_low_defaults()
        return ModeConfig(
            mode=MODE_LOW,
            model_id=os.environ.get("FLUX_LOW_MODEL_ID", "black-forest-labs/FLUX.2-klein-base-4B"),
            pipeline_cls=Flux2KleinPipeline,
            default_width=env_int("FLUX_LOW_WIDTH", width),
            default_height=env_int("FLUX_LOW_HEIGHT", height),
            default_steps=env_int("FLUX_LOW_STEPS", steps),
            default_guidance_scale=env_float("FLUX_LOW_GUIDANCE_SCALE", guidance),
        )
    if mode == MODE_FAST:
        width, height, steps, guidance = choose_fast_defaults()
        return ModeConfig(
            mode=MODE_FAST,
            model_id=os.environ.get("FLUX_FAST_MODEL_ID", "black-forest-labs/FLUX.2-klein-4B"),
            pipeline_cls=Flux2KleinPipeline,
            default_width=env_int("FLUX_FAST_WIDTH", width),
            default_height=env_int("FLUX_FAST_HEIGHT", height),
            default_steps=env_int("FLUX_FAST_STEPS", steps),
            default_guidance_scale=env_float("FLUX_FAST_GUIDANCE_SCALE", guidance),
            gguf_path=os.environ.get(
                "FLUX_FAST_GGUF_PATH",
                r"B:\Models\unsloth\FLUX.2-klein-4B-GGUF\flux-2-klein-4b-BF16.gguf",
            ),
            gguf_config_repo=os.environ.get(
                "FLUX_FAST_GGUF_CONFIG_REPO",
                "black-forest-labs/FLUX.2-klein-4B",
            ),
        )
    if mode == MODE_HIGH:
        width, height = choose_high_resolution_defaults()
        return ModeConfig(
            mode=MODE_HIGH,
            model_id="black-forest-labs/FLUX.2-dev",
            pipeline_cls=Flux2Pipeline,
            default_width=width,
            default_height=height,
            default_steps=40,
            default_guidance_scale=3.5,
        )
    raise SystemExit(f"Unsupported FLUX_MODE '{mode}'. Use 'low', 'fast', or 'high'.")


class FluxRuntime:
    def __init__(self) -> None:
        self.generation_lock = threading.Lock()
        self.mode = os.environ.get("FLUX_MODE", MODE_LOW).strip().lower()
        self.load_strategy = "unknown"
        self.server_transport = "stdio"
        self.pipeline = None
        self.metrics = Metrics(
            server_started_at=utc_now_iso(),
            selected_mode=self.mode,
            selected_model_id="",
            load_strategy=self.load_strategy,
            server_transport=self.server_transport,
            cuda_available=torch.cuda.is_available(),
            cuda_version=torch.version.cuda,
            gpu_name=torch.cuda.get_device_name(0) if torch.cuda.is_available() else "",
            process_id=os.getpid(),
        )
        self.config = self._startup()

    def _startup(self) -> ModeConfig:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        HF_HOME_PATH.mkdir(parents=True, exist_ok=True)

        LOGGER.info("Python version: %s", sys.version.replace("\n", " "))
        LOGGER.info("torch version: %s", torch.__version__)
        LOGGER.info("CUDA available: %s", torch.cuda.is_available())
        LOGGER.info("CUDA version: %s", torch.version.cuda)

        if sys.version_info[:2] != (3, 12):
            LOGGER.warning(
                "Python 3.12 is recommended for this server. Detected %s.%s.",
                sys.version_info.major,
                sys.version_info.minor,
            )

        if not torch.cuda.is_available():
            raise SystemExit(
                "CUDA is unavailable. Install a CUDA-enabled PyTorch build and verify your NVIDIA driver."
            )

        gpu_name = torch.cuda.get_device_name(0)
        total_vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 3)
        free_vram_gb = get_free_vram_gb()
        LOGGER.info("GPU name: %s", gpu_name)
        LOGGER.info("GPU memory | total=%.3f GiB free=%s GiB", total_vram_gb, free_vram_gb)
        self.metrics.total_vram_gb = total_vram_gb
        self.metrics.free_vram_at_start_gb = free_vram_gb
        if free_vram_gb is not None and free_vram_gb < 6:
            LOGGER.warning(
                "Low free VRAM detected at startup (%.3f GiB). Other GPU-heavy apps will force more CPU offload and can make generations extremely slow.",
                free_vram_gb,
            )

        config = get_mode_config(self.mode)
        self.metrics.selected_model_id = config.model_id

        if self.mode == MODE_HIGH:
            LOGGER.warning(
                "High mode selected. FLUX.2-dev can be very slow on consumer GPUs and may require a large download."
            )

        LOGGER.info("HF_HOME: %s", os.environ.get("HF_HOME"))
        LOGGER.info("HF_HUB_DISABLE_XET: %s", os.environ.get("HF_HUB_DISABLE_XET"))
        LOGGER.info(
            "Loading model '%s' with pipeline %s",
            config.model_id,
            config.pipeline_cls.__name__,
        )

        try:
            self.pipeline = self._load_pipeline(config)
            self.load_strategy = self._configure_pipeline_placement(total_vram_gb, free_vram_gb)
            self.metrics.load_strategy = self.load_strategy

            if hasattr(self.pipeline, "enable_vae_tiling"):
                self.pipeline.enable_vae_tiling()
            if hasattr(self.pipeline, "enable_vae_slicing"):
                self.pipeline.enable_vae_slicing()
            if hasattr(self.pipeline, "set_progress_bar_config"):
                self.pipeline.set_progress_bar_config(disable=True)
        except Exception as exc:
            raise SystemExit(f"Failed to load model '{config.model_id}': {exc}") from exc

        torch.cuda.empty_cache()
        LOGGER.info(
            "Server ready. Mode=%s Model=%s Default=%sx%s steps=%s guidance=%s",
            config.mode,
            config.model_id,
            config.default_width,
            config.default_height,
            config.default_steps,
            config.default_guidance_scale,
        )
        return config

    def _load_pipeline(self, config: ModeConfig) -> Any:
        if not config.gguf_path:
            return config.pipeline_cls.from_pretrained(
                config.model_id,
                torch_dtype=config.dtype,
            )

        gguf_path = Path(config.gguf_path)
        if not gguf_path.exists():
            raise SystemExit(
                f"Configured FLUX fast GGUF file was not found: {gguf_path}"
            )
        if importlib.util.find_spec("gguf") is None:
            raise SystemExit(
                "The gguf package is required for FLUX_MODE=fast. Install it with: python -m pip install gguf"
            )
        if not config.gguf_config_repo:
            raise SystemExit("FLUX fast GGUF mode requires a config repo id.")

        transformer = Flux2Transformer2DModel.from_single_file(
            str(gguf_path),
            quantization_config=GGUFQuantizationConfig(compute_dtype=config.dtype),
            config=config.gguf_config_repo,
            subfolder="transformer",
            torch_dtype=config.dtype,
        )
        return config.pipeline_cls.from_pretrained(
            config.model_id,
            transformer=transformer,
            torch_dtype=config.dtype,
        )

    def _configure_pipeline_placement(
        self,
        total_vram_gb: float,
        free_vram_gb: float | None,
    ) -> str:
        requested_strategy = os.environ.get("FLUX_LOAD_STRATEGY", "auto").strip().lower()
        if requested_strategy not in {"auto", "cuda", "cpu_offload"}:
            raise SystemExit(
                "Unsupported FLUX_LOAD_STRATEGY. Use 'auto', 'cuda', or 'cpu_offload'."
            )

        actual_strategy = requested_strategy
        if requested_strategy == "auto":
            can_try_full_cuda = (
                (
                    self.mode == MODE_LOW
                    and total_vram_gb >= 13
                    and free_vram_gb is not None
                    and free_vram_gb >= 10
                )
                or (
                    self.mode == MODE_FAST
                    and total_vram_gb >= 12
                    and free_vram_gb is not None
                    and free_vram_gb >= 9
                )
            )
            actual_strategy = "cuda" if can_try_full_cuda else "cpu_offload"

        try:
            if actual_strategy == "cuda":
                self.pipeline.to("cuda")
                LOGGER.info("Pipeline placement: full CUDA")
                return "cuda"
            self.pipeline.enable_model_cpu_offload()
            LOGGER.info("Pipeline placement: CPU offload")
            return "cpu_offload"
        except torch.cuda.OutOfMemoryError:
            LOGGER.warning(
                "Full CUDA placement ran out of memory. Falling back to CPU offload."
            )
            torch.cuda.empty_cache()
            self.pipeline.enable_model_cpu_offload()
            return "cpu_offload"

    def _build_generation_kwargs(
        self,
        *,
        prompt: str,
        width: int,
        height: int,
        steps: int,
        guidance_scale: float,
        generator: torch.Generator,
        negative_prompt: str | None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": steps,
            "guidance_scale": guidance_scale,
            "generator": generator,
        }

        if negative_prompt is not None:
            negative_prompt = negative_prompt.strip()
        if not negative_prompt:
            return kwargs

        call_params = inspect.signature(self.pipeline.__call__).parameters
        if "negative_prompt" in call_params:
            kwargs["negative_prompt"] = negative_prompt
            return kwargs
        if "negative_prompt_embeds" in call_params:
            if not hasattr(self.pipeline, "encode_prompt"):
                raise ValueError(
                    f"{type(self.pipeline).__name__} exposes negative_prompt_embeds but does not provide encode_prompt."
                )

            negative_prompt_embeds, _ = self.pipeline.encode_prompt(
                prompt=negative_prompt,
                num_images_per_prompt=1,
            )
            kwargs["negative_prompt_embeds"] = negative_prompt_embeds
            return kwargs

        raise ValueError(
            f"negative_prompt is not supported by {type(self.pipeline).__name__} in the installed diffusers build."
        )

    def generate(
        self,
        *,
        prompt: str,
        negative_prompt: str | None,
        width: int | None,
        height: int | None,
        steps: int | None,
        guidance_scale: float | None,
        seed: int | None,
        output_name: str | None,
    ) -> dict[str, Any]:
        if not prompt or not prompt.strip():
            raise ValueError("prompt is required.")

        width = width or self.config.default_width
        height = height or self.config.default_height
        steps = steps or self.config.default_steps
        guidance_scale = guidance_scale if guidance_scale is not None else self.config.default_guidance_scale
        seed = seed if seed is not None else secrets.randbelow(2**31 - 1)

        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive integers.")
        if steps <= 0:
            raise ValueError("steps must be a positive integer.")
        if guidance_scale < 0:
            raise ValueError("guidance_scale must be non-negative.")

        output_filename = sanitize_output_name(output_name, self.mode, seed)
        output_path = (OUTPUT_DIR / output_filename).resolve()

        LOGGER.info(
            "Request started | mode=%s model=%s size=%sx%s steps=%s guidance=%s seed=%s output=%s",
            self.mode,
            self.config.model_id,
            width,
            height,
            steps,
            guidance_scale,
            seed,
            output_path,
        )
        LOGGER.info("Prompt: %s", prompt)
        if negative_prompt:
            LOGGER.info("Negative prompt: %s", negative_prompt)

        with self.generation_lock:
            start = time.perf_counter()
            self.metrics.is_generating = True
            self.metrics.current_request_started_at = utc_now_iso()
            generator = torch.Generator(device="cuda").manual_seed(seed)
            generation_kwargs = self._build_generation_kwargs(
                prompt=prompt,
                width=width,
                height=height,
                steps=steps,
                guidance_scale=guidance_scale,
                generator=generator,
                negative_prompt=negative_prompt,
            )

            try:
                torch.cuda.synchronize()
                with torch.inference_mode():
                    image = self.pipeline(**generation_kwargs).images[0]
                torch.cuda.synchronize()
                elapsed = time.perf_counter() - start
                image.save(output_path, format="PNG")
            except Exception as exc:
                LOGGER.exception("Generation failed.")
                raise RuntimeError(f"Image generation failed: {exc}") from exc
            finally:
                self.metrics.is_generating = False
                self.metrics.current_request_started_at = None
                torch.cuda.empty_cache()

        self.metrics.total_images_generated += 1
        self.metrics.last_generation_seconds = round(elapsed, 3)
        self.metrics.generation_history.append(elapsed)
        self.metrics.average_generation_seconds = round(
            statistics.fmean(self.metrics.generation_history),
            3,
        )
        self.metrics.last_generated_at = utc_now_iso()
        self.metrics.last_output_path = str(output_path)

        LOGGER.info(
            "Request finished | elapsed=%.3fs total_images=%s output=%s",
            elapsed,
            self.metrics.total_images_generated,
            output_path,
        )

        return {
            "output_path": str(output_path),
            "elapsed_seconds": round(elapsed, 3),
            "model_used": self.config.model_id,
            "mode_used": self.mode,
            "seed_used": seed,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale": guidance_scale,
        }

    def status(self) -> dict[str, Any]:
        return {
            "server_started_at": self.metrics.server_started_at,
            "selected_mode": self.metrics.selected_mode,
            "selected_model_id": self.metrics.selected_model_id,
            "load_strategy": self.metrics.load_strategy,
            "server_transport": self.metrics.server_transport,
            "cuda_available": self.metrics.cuda_available,
            "cuda_version": self.metrics.cuda_version,
            "gpu_name": self.metrics.gpu_name,
            "total_vram_gb": self.metrics.total_vram_gb,
            "free_vram_at_start_gb": self.metrics.free_vram_at_start_gb,
            "process_id": self.metrics.process_id,
            "is_generating": self.metrics.is_generating,
            "current_request_started_at": self.metrics.current_request_started_at,
            "torch_version": torch.__version__,
            "python_version": sys.version.split()[0],
            "hf_home": os.environ.get("HF_HOME"),
            "hf_hub_disable_xet": os.environ.get("HF_HUB_DISABLE_XET"),
            "output_dir": str(OUTPUT_DIR.resolve()),
            "fast_gguf_path": self.config.gguf_path,
            "streamable_http_host": mcp.settings.host,
            "streamable_http_port": mcp.settings.port,
            "streamable_http_path": mcp.settings.streamable_http_path,
            "default_width": self.config.default_width,
            "default_height": self.config.default_height,
            "default_steps": self.config.default_steps,
            "default_guidance_scale": self.config.default_guidance_scale,
            "total_images_generated": self.metrics.total_images_generated,
            "last_generation_seconds": self.metrics.last_generation_seconds,
            "average_generation_seconds": self.metrics.average_generation_seconds,
            "last_generated_at": self.metrics.last_generated_at,
            "last_output_path": self.metrics.last_output_path,
        }


RUNTIME = FluxRuntime()


@mcp.tool()
def generate_image(
    prompt: str,
    negative_prompt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    steps: int | None = None,
    guidance_scale: float | None = None,
    seed: int | None = None,
    output_name: str | None = None,
) -> dict[str, Any]:
    """Generate an image with the single FLUX model loaded at server startup."""
    return RUNTIME.generate(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        steps=steps,
        guidance_scale=guidance_scale,
        seed=seed,
        output_name=output_name,
    )


@mcp.tool()
def flux_status() -> dict[str, Any]:
    """Return runtime status and generation metrics for the FLUX MCP server."""
    return RUNTIME.status()


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def http_health(_request) -> JSONResponse:
    status = RUNTIME.status()
    payload = {
        "ok": True,
        "mode": status["selected_mode"],
        "model_id": status["selected_model_id"],
        "transport": status["server_transport"],
        "is_generating": status["is_generating"],
        "process_id": status["process_id"],
        "mcp_endpoint": (
            f"http://{status['streamable_http_host']}:{status['streamable_http_port']}"
            f"{status['streamable_http_path']}"
        ),
    }
    return JSONResponse(payload)


@mcp.custom_route("/status", methods=["GET"], include_in_schema=False)
async def http_status(_request) -> JSONResponse:
    return JSONResponse(RUNTIME.status())


@mcp.custom_route("/", methods=["GET"], include_in_schema=False)
async def http_dashboard(_request) -> HTMLResponse:
    status_url = "/status"
    health_url = "/health"
    mcp_path = escape(mcp.settings.streamable_http_path)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>FLUX MCP Service</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #f2efe8;
      --panel: #fffdf8;
      --ink: #1f1e1a;
      --muted: #6b665b;
      --warn: #b45309;
      --border: #d9d2c5;
      --code: #f6f1e7;
      --hero: #efe6d8;
      --pill-bg: #d1fae5;
      --pill-ink: #065f46;
      --pill-busy-bg: #fef3c7;
      --pill-busy-ink: #b45309;
      color-scheme: light;
    }}
    :root[data-theme="dark"] {{
      --bg: #11161c;
      --panel: #18212b;
      --ink: #edf3f8;
      --muted: #95a5b6;
      --border: #2a3744;
      --code: #0f151b;
      --hero: #0c1116;
      --pill-bg: #11382f;
      --pill-ink: #8df0c6;
      --pill-busy-bg: #4b3411;
      --pill-busy-ink: #ffd38b;
      color-scheme: dark;
    }}
    body {{
      margin: 0;
      padding: 24px;
      background: linear-gradient(180deg, var(--hero) 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: "Segoe UI", "Trebuchet MS", sans-serif;
    }}
    .wrap {{
      max-width: 980px;
      margin: 0 auto;
    }}
    .hero {{
      display: grid;
      gap: 12px;
      margin-bottom: 18px;
    }}
    .hero-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .title {{
      font-size: 30px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .sub {{
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 10px 30px rgba(31, 30, 26, 0.06);
    }}
    .label {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 6px;
    }}
    .value {{
      font-size: 22px;
      font-weight: 700;
    }}
    .mono {{
      font-family: Consolas, "Courier New", monospace;
      background: var(--code);
      padding: 2px 6px;
      border-radius: 6px;
    }}
    .status {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--pill-bg);
      color: var(--pill-ink);
      font-weight: 700;
    }}
    .status.busy {{
      background: var(--pill-busy-bg);
      color: var(--pill-busy-ink);
    }}
    .theme-toggle {{
      border: 1px solid var(--border);
      background: var(--panel);
      color: var(--ink);
      border-radius: 999px;
      padding: 9px 14px;
      font: inherit;
      cursor: pointer;
    }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.45;
    }}
    .footer {{
      margin-top: 16px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="hero-row">
        <div class="title">FLUX MCP Service</div>
        <button id="theme-toggle" class="theme-toggle" type="button">Dark Mode</button>
      </div>
      <div class="sub">Persistent local service for Goose. MCP endpoint <span class="mono">{mcp_path}</span></div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="label">Service</div>
        <div id="service-state" class="status">Loading</div>
      </div>
      <div class="card">
        <div class="label">Mode</div>
        <div id="mode" class="value">-</div>
      </div>
      <div class="card">
        <div class="label">Model</div>
        <div id="model" class="value" style="font-size:16px">-</div>
      </div>
      <div class="card">
        <div class="label">Images Generated</div>
        <div id="count" class="value">0</div>
      </div>
      <div class="card">
        <div class="label">Last Duration</div>
        <div id="last-seconds" class="value">-</div>
      </div>
      <div class="card">
        <div class="label">GPU / Load Strategy</div>
        <div id="gpu" class="value" style="font-size:16px">-</div>
      </div>
    </div>

    <div class="card">
      <div class="label">Live Status JSON</div>
      <pre id="json">Loading...</pre>
    </div>

    <div class="footer">
      Health: <span class="mono">{escape(health_url)}</span> |
      Status: <span class="mono">{escape(status_url)}</span> |
      Refresh: every 3 seconds
    </div>
  </div>

  <script>
    const root = document.documentElement;
    const savedTheme = localStorage.getItem("flux-dashboard-theme") || "light";
    root.setAttribute("data-theme", savedTheme);

    const toggle = document.getElementById("theme-toggle");
    function syncThemeButton() {{
      const theme = root.getAttribute("data-theme") || "light";
      toggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }}
    toggle.addEventListener("click", () => {{
      const current = root.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("flux-dashboard-theme", next);
      syncThemeButton();
    }});
    syncThemeButton();

    async function refresh() {{
      try {{
        const response = await fetch("{status_url}", {{ cache: "no-store" }});
        const status = await response.json();
        const state = document.getElementById("service-state");
        state.textContent = status.is_generating ? "Generating" : "Ready";
        state.className = status.is_generating ? "status busy" : "status";
        document.getElementById("mode").textContent = status.selected_mode;
        document.getElementById("model").textContent = status.selected_model_id;
        document.getElementById("count").textContent = status.total_images_generated;
        document.getElementById("last-seconds").textContent =
          status.last_generation_seconds == null ? "-" : status.last_generation_seconds + "s";
        document.getElementById("gpu").textContent =
          status.gpu_name + " / " + status.load_strategy;
        document.getElementById("json").textContent = JSON.stringify(status, null, 2);
      }} catch (error) {{
        const state = document.getElementById("service-state");
        state.textContent = "Unavailable";
        state.className = "status busy";
        document.getElementById("json").textContent = String(error);
      }}
    }}
    refresh();
    setInterval(refresh, 3000);
  </script>
</body>
</html>
"""
    return HTMLResponse(html)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FLUX MCP server")
    parser.add_argument(
        "--transport",
        choices=("stdio", "streamable-http"),
        default=os.environ.get("FLUX_TRANSPORT", "stdio"),
        help="MCP transport to use.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("FLUX_HTTP_HOST", "127.0.0.1"),
        help="Host for streamable HTTP transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("FLUX_HTTP_PORT", "8765")),
        help="Port for streamable HTTP transport.",
    )
    parser.add_argument(
        "--streamable-http-path",
        default=os.environ.get("FLUX_HTTP_PATH", "/mcp"),
        help="Path for the MCP streamable HTTP endpoint.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.transport == "streamable-http":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.settings.streamable_http_path = args.streamable_http_path
        RUNTIME.server_transport = "streamable-http"
        RUNTIME.metrics.server_transport = "streamable-http"
        LOGGER.info(
            "Starting MCP streamable HTTP service at http://%s:%s%s",
            args.host,
            args.port,
            args.streamable_http_path,
        )
        LOGGER.info(
            "Dashboard available at http://%s:%s/",
            args.host,
            args.port,
        )
        mcp.run(transport="streamable-http")
        return

    RUNTIME.server_transport = "stdio"
    RUNTIME.metrics.server_transport = "stdio"
    LOGGER.info("Starting MCP stdio server.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
