# MEMORY.md - FluxImageGen Project Index

## Project Status
- **Working Directory**: `B:/Pond/FluxImageGen`
- **Project**: FLUX image generation tool (MCP server + Python scripts)
- **Git**: Initialized, user configured (`goose / goose@aaif.ai`)
- **Setup Date**: 2026-04-26
- **Session Count**: 2

## Tech Stack
- Python 3.x
- Diffusers-based FLUX image generation
- MCP server (`mcp_flux_server.py`)
- Persistent MCP HTTP service (`streamable-http`)
- PowerShell + batch service launchers
- Diffusers GGUF loading for local fast mode

## Project Structure
```text
FluxImageGen/
|-- README.md                     # Project overview
|-- MEMORY.md                     # This file (primary index)
|-- .goosehints                   # Best practices & guidelines
|-- goosehints.md                 # Expanded system prompt
|-- requirements.txt              # Python dependencies
|-- mcp_flux_server.py            # MCP server for FLUX
|-- start_flux_service.ps1        # Persistent HTTP service launcher
|-- stop_flux_service.ps1         # Persistent HTTP service stopper
|-- status_flux_service.ps1       # Service status + log summary
|-- monitor_flux_service.ps1      # Live log tail for service
|-- run_flux_klein.py             # Main runner (standard quality)
|-- run_flux_klein_high.py        # Main runner (high quality)
|-- start_flux_low.bat            # Batch launcher - low quality
|-- start_flux_high.bat           # Batch launcher - high quality
|-- start_flux_menu.bat           # Batch launcher - menu
|-- promptforphoto.txt            # Prompt input file
|-- flux-image-project-plan.md    # Project plan document
|-- example_mcp_config.json       # MCP config example
|-- flux_output/                  # Generated images output
|-- .flux-service/                # Per-port PID, metadata, and logs
|-- recipes/                      # Goose recipe files
`-- .goose/                       # Goose internal config
```

## Topic Files
- `flux-image-project-plan.md` - Project plan and goals
- `promptforphoto.txt` - Current photo prompt

## Recent Tasks
1. **[2026-04-26]** Workspace initialization: copied goosehints, initialized git, created MEMORY.md
2. **[2026-04-27]** Converted MCP server to persistent `streamable-http` service with dashboard, health/status endpoints, and Windows start/stop/status/monitor scripts
3. **[2026-04-27]** Added `fast` mode using local GGUF transformer at `B:\Models\unsloth\FLUX.2-klein-4B-GGUF\flux-2-klein-4b-BF16.gguf`
4. **[2026-04-27]** Added dashboard dark-mode toggle with browser-persisted theme setting
5. **[2026-04-27]** Verified Goose is hitting the persistent service and observed that Goose can override server-side default image size

## Pending Tasks
- Optional: benchmark `fast` vs `low` generation times on the 12 GB RTX 4070
- Optional: add request clamping for `fast` mode so Goose cannot silently force `1024x1024`

## Next Session Instructions
- Follow `.goosehints` guidelines
- Use PowerShell for shell commands on this Windows machine
- Verify file state before making changes
- Goose should use the persistent remote MCP endpoint `http://127.0.0.1:8765/mcp`, not the old `stdio` FLUX extension
- Current recommended service command: `.\start_flux_service.ps1 -Mode fast`
- Dashboard: `http://127.0.0.1:8765/`
- Status JSON: `http://127.0.0.1:8765/status`
- Service scripts use per-port PID, metadata, and log files under `.flux-service/`

## Schema Notes
- N/A (no database in this project)

## Notes
- FLUX server now supports both `stdio` and persistent `streamable-http` transport
- Persistent service exposes:
  - `/` dashboard
  - `/health`
  - `/status`
  - `/mcp` streamable HTTP MCP endpoint
- Current verified runtime mode is `fast` on port `8765`
- `fast` mode uses `black-forest-labs/FLUX.2-klein-4B` plus local GGUF transformer weights
- Even in `fast` mode, the 12 GB RTX 4070 still falls back to `cpu_offload`; the GGUF file alone does not make the full pipeline fit entirely on GPU
- Verified `fast` mode defaults are `640x640`, `4` steps, `guidance_scale=1.0`
- Verified Goose can override server defaults; a live request used `1024x1024` while still running in `fast` mode
- Output images are saved to `flux_output/`
