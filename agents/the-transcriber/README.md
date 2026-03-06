# The Transcriber -- Speech-to-Text for Agents

The compute layer of the agent economy. Local-model speech-to-text on Apple Silicon using NVIDIA Parakeet. The only agent providing real ML compute, not an API proxy.

**Port:** 3900

## Why This Exists

Every other agent in the marketplace wraps an API call. The Transcriber actually runs an ML model on local hardware. Your agent is in a Lambda, a container, a serverless function -- you can't download a 1GB model. Pay us, get a transcript back in seconds.

Real compute as a service for the agent economy.

## Tools (All FREE)

| Tool | Description |
|------|-------------|
| `transcribe_youtube` | YouTube URL -> full text transcript. Downloads audio automatically. |
| `transcribe_file` | Audio/video file -> full text transcript. Supports wav, mp3, m4a, flac, ogg, mp4, mkv, webm. |
| `transcriber_info` | Service capabilities, model info, and supported formats. |

### Honest Limitations

- Requires Apple Silicon Mac (M1/M2/M3/M4) for the Parakeet MLX model.
- Transcription accuracy depends on audio quality. Noisy recordings, heavy accents, or overlapping speakers will reduce accuracy.
- YouTube downloads depend on yt-dlp, which may break if YouTube changes their API.
- Large files (>1hr) may take significant time and memory.
- English-optimized. Other languages may work but with lower accuracy.

## Prerequisites

```bash
# Apple Silicon required
pip install parakeet-mlx    # NVIDIA Parakeet for MLX
pip install yt-dlp           # YouTube download support
```

## Quick Start

```bash
cd agents/the-transcriber
cp .env.example .env    # Add your NVM_API_KEY
poetry install
poetry run python -m src.setup   # Register on Nevermined (one-time)
poetry run python -m src.server  # Starts on port 3900
```

## Endpoints

| Path | Description |
|------|-------------|
| `/mcp` | MCP protocol endpoint |
| `/health` | Health check |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NVM_API_KEY` | Yes | Nevermined API key |
| `NVM_ENVIRONMENT` | No | Default: `sandbox` |
| `NVM_AGENT_ID` | Auto | Set by `src.setup` |
| `NVM_PLAN_ID` | Auto | Set by `src.setup` |
| `PORT` | No | Default: `3900` |

## Part of the Agent Economy

The Transcriber is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It's unique in the portfolio -- while other services provide information infrastructure (discovery, trust, quality), The Transcriber provides actual compute infrastructure.
