# MEMORY.md - FluxImageGen Project Index

## Project Status
- **Working Directory**: `B:/Pond/FluxImageGen`
- **Project**: FLUX image generation tool (MCP server + Python scripts)
- **Git**: Initialized, user configured (`goose / goose@aaif.ai`)
- **Setup Date**: 2026-04-26
- **Session Count**: 1

## Tech Stack
- Python 3.x
- FLUX image generation models (single model loaded at server startup)
- MCP server (`mcp_flux_server.py`)
- Batch launchers (`start_flux_*.bat`)

## Project Structure
```
FluxImageGen/
├── README.md                     # Project overview
├── MEMORY.md                     # This file (primary index)
├── .goosehints                   # Best practices & guidelines
├── goosehints.md                 # Expanded system prompt
├── requirements.txt              # Python dependencies
├── mcp_flux_server.py            # MCP server for FLUX
├── run_flux_klein.py             # Main runner (standard quality)
├── run_flux_klein_high.py        # Main runner (high quality)
├── start_flux_low.bat            # Batch launcher - low quality
├── start_flux_high.bat           # Batch launcher - high quality
├── start_flux_menu.bat           # Batch launcher - menu
├── promptforphoto.txt            # Prompt input file
├── flux-image-project-plan.md    # Project plan document
├── example_mcp_config.json       # MCP config example
├── flux_output/                  # Generated images output
├── recipes/                      # Goose recipe files (4 recipes)
└── .goose/                       # Goose internal config
```

## Topic Files
- `flux-image-project-plan.md` - Project plan and goals
- `promptforphoto.txt` - Current photo prompt

## Recent Tasks
1. **[2026-04-26]** Workspace initialization: copied goosehints, initialized git, created MEMORY.md

## Pending Tasks
- None yet

## Next Session Instructions
- Follow `.goosehints` guidelines
- Use PowerShell for shell commands (Windows machine)
- Verify file state before making changes (Skeptical Memory)

## Schema Notes
- N/A (no database in this project)

## Notes
- FLUX server generates images via single model loaded at startup
- Two quality modes: standard (`run_flux_klein.py`) and high (`run_flux_klein_high.py`)
- Output images saved to `flux_output/` directory
