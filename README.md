# FLUX MCP Server

Local Windows MCP server for FLUX image generation with Hugging Face Diffusers.

It exposes two MCP tools:

- `generate_image`
- `flux_status`

The server loads exactly one model at startup based on `FLUX_MODE` and keeps that model in memory for the lifetime of the process.

It can run in two transports:

- `stdio` for one-off local child-process use
- `streamable-http` for a persistent Goose-ready service

## Files

- `mcp_flux_server.py`: MCP stdio server.
- `requirements.txt`: Python dependencies, including a CUDA PyTorch wheel source.
- `start_flux_low.bat`: Starts low mode.
- `start_flux_high.bat`: Starts high mode.
- `start_flux_menu.bat`: Menu launcher for double-click use.
- `example_mcp_config.json`: Example Claude Code JSON plus Goose equivalents.

## Modes

### Low / fast

- Model: `black-forest-labs/FLUX.2-klein-base-4B`
- Pipeline: `Flux2KleinPipeline`
- Defaults:
  - `width=1024`, `height=1024`, `steps=32` on GPUs with 16 GB+ VRAM
  - `width=704`, `height=704`, `steps=16` on GPUs with 12 GB to under 16 GB VRAM
  - `width=640`, `height=640`, `steps=12` on GPUs under 12 GB VRAM
  - `guidance_scale=1.5` on 12 GB+ profiles, `1.25` under 12 GB
  - `dtype=torch.bfloat16`
  - `FLUX_LOAD_STRATEGY=auto` by default:
    - uses full CUDA only when low mode has enough free VRAM at startup
    - otherwise falls back to `enable_model_cpu_offload()`

On a 12 GB GPU, `flux-low` now defaults to the 704x704 / 16-step profile because the 4B Klein checkpoint is right on the edge of 12 GB cards and can become extremely slow when other apps are already using VRAM.

### Fast / GGUF

- Model: local GGUF transformer plus `black-forest-labs/FLUX.2-klein-4B`
- Pipeline: `Flux2KleinPipeline`
- Default local GGUF path:
  - `B:\Models\unsloth\FLUX.2-klein-4B-GGUF\flux-2-klein-4b-BF16.gguf`
- Defaults:
  - `width=1024`, `height=1024`, `steps=4`, `guidance_scale=1.0` on GPUs with 16 GB+ VRAM
  - `width=768`, `height=768`, `steps=4`, `guidance_scale=1.0` on GPUs with 12 GB to under 16 GB VRAM
  - `width=640`, `height=640`, `steps=4`, `guidance_scale=1.0` on GPUs under 12 GB VRAM
  - `dtype=torch.bfloat16`
  - uses Diffusers GGUF loading for the transformer, then builds the rest of the pipeline from `black-forest-labs/FLUX.2-klein-4B`

Notes:

- This mode requires the `gguf` Python package.
- The `.gguf` file is only the transformer weights; the rest of the pipeline still loads separately.
- On this project machine, fast mode starts successfully but still falls back to CPU offload on a 12 GB RTX 4070, so it reduces steps dramatically but does not fully eliminate offload.

### High / quality

- Model: `black-forest-labs/FLUX.2-dev`
- Pipeline: `Flux2Pipeline`
- Defaults:
  - `width=768` on GPUs under 16 GB VRAM, otherwise `1024`
  - `height=768` on GPUs under 16 GB VRAM, otherwise `1024`
  - `steps=40`
  - `guidance_scale=3.5`
  - `dtype=torch.bfloat16`
  - `enable_model_cpu_offload()`

## Environment

The server sets these defaults if they are not already present:

- `HF_HOME=B:\Pond\hf_cache`
- `HF_HUB_DISABLE_XET=1`
- `FLUX_LOAD_STRATEGY=auto`

Optional low-mode overrides:

- `FLUX_LOW_MODEL_ID`
- `FLUX_LOW_WIDTH`
- `FLUX_LOW_HEIGHT`
- `FLUX_LOW_STEPS`
- `FLUX_LOW_GUIDANCE_SCALE`

Optional fast-mode overrides:

- `FLUX_FAST_MODEL_ID`
- `FLUX_FAST_GGUF_PATH`
- `FLUX_FAST_GGUF_CONFIG_REPO`
- `FLUX_FAST_WIDTH`
- `FLUX_FAST_HEIGHT`
- `FLUX_FAST_STEPS`
- `FLUX_FAST_GUIDANCE_SCALE`

Images are written to:

- `B:\Pond\FluxImageGen\flux_output`

## Setup

Python `3.12` is the target for this project.

### 1. Create a venv

```powershell
py -3.12 -m venv flux-env312
.\flux-env312\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If your PyTorch install ends up CPU-only, reinstall it with the CUDA wheel source from `requirements.txt`.

### 3. Start the server

Manual launcher:

```powershell
.\start_flux_menu.bat
```

The batch launchers auto-detect the first existing venv in this order:

- `flux-env-cu`
- `flux-env312`
- `.venv`
- `venv`
- `flux-env`
- `flux-env311`

Or directly:

```powershell
$env:FLUX_MODE = "low"
$env:HF_HOME = "B:\Pond\hf_cache"
$env:HF_HUB_DISABLE_XET = "1"
python .\mcp_flux_server.py
```

## Persistent Service For Goose

Recommended for Goose. This keeps the model loaded in one background process instead of tying it to a single Goose session.

### Start the service

PowerShell:

```powershell
.\start_flux_service.ps1 -Mode low
```

For the local GGUF-backed fast mode:

```powershell
.\start_flux_service.ps1 -Mode fast
```

Batch wrapper:

```powershell
.\start_flux_service.bat -Mode low
```

Convenience batch launchers:

```powershell
.\start_flux_fast.bat
.\start_flux_low.bat
.\start_flux_high.bat
.\start_flux_menu.bat
```

Default service URLs:

- Dashboard: `http://127.0.0.1:8765/`
- Health: `http://127.0.0.1:8765/health`
- Status JSON: `http://127.0.0.1:8765/status`
- Goose MCP endpoint: `http://127.0.0.1:8765/mcp`

The start script:

- checks whether a healthy FLUX service is already running on that port
- refuses to start if the port is occupied by something else
- writes logs under `.flux-service\`
- waits until the model is loaded and the service is healthy before reporting success

### Monitor the service

Quick status:

```powershell
.\status_flux_service.ps1
```

Live log tail:

```powershell
.\monitor_flux_service.ps1
```

### Stop the service

```powershell
.\stop_flux_service.ps1
```

### Goose changes

Replace the old command-line `stdio` extension with a remote extension:

1. Run `goose configure`
2. Choose `Add Extension`
3. Choose `Remote Extension (Streamable HTTP)`
4. Name it something like `flux-low`
5. Set endpoint to `http://127.0.0.1:8765/mcp`
6. Set timeout to `3600` seconds
7. Disable or remove the old `stdio` FLUX extension so Goose does not start a second server process

If you want Goose to use the fast GGUF-backed mode, start the service with `-Mode fast` before launching Goose. The Goose endpoint stays the same.

Goose documentation for remote streamable HTTP extensions:

- https://goose-docs.ai/docs/getting-started/using-extensions/

### Legacy stdio launchers

For manual debugging only, the old foreground `stdio` launchers are still available as:

- `start_flux_low_stdio_legacy.bat`
- `start_flux_high_stdio_legacy.bat`

Do not run those at the same time as the persistent service Goose uses.

## MCP tools

### `generate_image`

Inputs:

- `prompt` (required)
- `negative_prompt` (optional)
- `width` (optional)
- `height` (optional)
- `steps` (optional)
- `guidance_scale` (optional)
- `seed` (optional)
- `output_name` (optional)

Returns:

- absolute output PNG path
- elapsed seconds
- model used
- mode used
- seed used
- dimensions
- steps
- guidance scale

### `flux_status`

Returns runtime metrics including:

- server start time
- selected mode
- selected model id
- CUDA availability
- CUDA version
- GPU name
- total images generated

When running in persistent HTTP mode, the same status is also available at:

- `GET /status`
- last generation time
- average generation time
- last output path

## Claude Code

Claude Code project config uses `.mcp.json`. A ready-made example is in `example_mcp_config.json`.

You can also add the server from the CLI with a JSON blob:

```powershell
claude mcp add-json flux-low "{`"type`":`"stdio`",`"command`":`"B:\\Pond\\FluxImageGen\\flux-env-cu\\Scripts\\python.exe`",`"args`":[`"B:\\Pond\\FluxImageGen\\mcp_flux_server.py`"],`"env`":{`"FLUX_MODE`":`"low`",`"HF_HOME`":`"B:\\Pond\\hf_cache`",`"HF_HUB_DISABLE_XET`":`"1`"}}"
```

## Goose

Goose stores persistent extension config in YAML, not JSON. The JSON example file includes CLI examples, and the equivalent persisted Goose config looks like this:

```yaml
extensions:
  flux-low:
    name: FLUX Low
    cmd: B:\Pond\FluxImageGen\flux-env-cu\Scripts\python.exe
    args:
      - B:\Pond\FluxImageGen\mcp_flux_server.py
    enabled: true
    envs:
      FLUX_MODE: low
      HF_HOME: B:\Pond\hf_cache
      HF_HUB_DISABLE_XET: "1"
    type: stdio
    timeout: 1800
```

One-shot Goose CLI example:

```powershell
goose session --with-extension "FLUX_MODE=low HF_HOME=B:\Pond\hf_cache HF_HUB_DISABLE_XET=1 B:\Pond\FluxImageGen\flux-env-cu\Scripts\python.exe B:\Pond\FluxImageGen\mcp_flux_server.py"
```

## Notes

- The server fails fast if CUDA is unavailable.
- The server fails fast if model loading fails.
- High mode logs a startup warning because `FLUX.2-dev` is slower and larger.
- Logging is sent to `stderr` so stdio MCP clients are not corrupted.
- `torch.inference_mode()` wraps generation.
- `torch.cuda.empty_cache()` runs after each generation.
- Output filenames are sanitized for Windows and saved as PNG.
- Requests are serialized with a lock so the shared pipeline is not used concurrently.

## Current limitation

With the currently installed `diffusers` `Flux2Pipeline`, `negative_prompt` is not exposed in high mode. If you pass a negative prompt while `FLUX_MODE=high`, the tool returns a clear error instead of silently ignoring it.
