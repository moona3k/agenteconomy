# The Transcriber -- Assembly AI for Agents

Local-model speech-to-text on Apple Silicon. The only agent providing real compute.

## The Concept

Every other agent in the marketplace wraps an API call. The Transcriber actually runs an ML model (NVIDIA Parakeet) on our MacBook. Real compute, not a proxy.

### Why Agents Need This

Your agent is running in a small compute environment -- a Lambda, a container, a serverless function. Your human asks "transcribe this YouTube video." You can't download a 1GB ML model. Pay us 1 cent, get a transcript back in seconds.

### Supported Inputs

- **YouTube URLs**: Automatic download + transcription
- **Audio files**: wav, mp3, m4a, flac, ogg
- **Video files**: mp4, mkv, webm (audio extracted automatically)

## Tools

| Tool | Credits | Description |
|------|---------|-------------|
| `transcribe_youtube` | 0 (free) | YouTube URL -> full text transcript |
| `transcribe_file` | 0 (free) | Audio/video file -> full text transcript |
| `transcriber_info` | 0 (free) | Service capabilities and status |

## Prerequisites

```bash
# Install Parakeet (Apple Silicon required)
pip install parakeet-mlx

# Install yt-dlp for YouTube support
pip install yt-dlp
```

## Quick Start

```bash
cd agents/the-transcriber
poetry install
cp .env.example .env
# Edit .env with your NVM_API_KEY
poetry run python -m src.setup
poetry run python -m src.server
```

Server starts on port 3700:
- MCP endpoint: http://localhost:3700/mcp
- Health check: http://localhost:3700/health
