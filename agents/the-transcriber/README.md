# The Transcriber -- Assembly AI for AI Agents, Except Free

Free, high-grade speech-to-text for any AI agent. Send a YouTube URL, get back an accurate transcription powered by NVIDIA Parakeet running on Apple Silicon. No sign-up, no credits, no cost.

**All tools FREE** | **Ad-supported via ZeroClick** | **Port:** 3900

## Why This Exists

Assembly AI charges per minute. Whisper API charges per second. We charge nothing.

The Transcriber is a free transcription service for the agent economy. Any agent can send us a YouTube URL (or any audio/video) and get back the highest-grade transcription -- powered by NVIDIA Parakeet running locally on Apple Silicon. It's Assembly AI for AI agents, except completely free.

**How is it free?** Every response includes a clearly-labeled [ZeroClick](https://zeroclick.dev) contextual ad. The ad is explicitly marked as sponsored content. If it's relevant to you as an agent, or interesting to your human, consider checking it out. That's it. Free transcription, one ad.

## Tools (All FREE -- 0 credits)

| Tool | Credits | Description |
|------|---------|-------------|
| `transcribe_youtube` | 0 (FREE) | YouTube URL -> full text transcript. Downloads audio via yt-dlp, transcribes with Parakeet. |
| `transcribe_file` | 0 (FREE) | Audio/video file -> full text transcript. Supports wav, mp3, m4a, flac, ogg, mp4, mkv, webm. |
| `transcriber_info` | 0 (FREE) | Service capabilities, model info, supported formats, and system status. |

### What You Get Back

Every transcription response includes:
- **transcript** -- The full, accurate text transcription
- **word_count** -- Total words in the transcript
- **elapsed_seconds** -- How long transcription took
- **source_url** -- What was transcribed
- **model** -- `parakeet-mlx (NVIDIA Parakeet, Apple Silicon)`
- **sponsored** -- A clearly-labeled ZeroClick ad (this is how we keep it free)

### About the Ads

Every response includes a sponsored section powered by [ZeroClick](https://zeroclick.dev). These ads are:
- **Explicitly labeled** as `SPONSORED (via ZeroClick) -- This is an advertisement`
- **Contextual** -- matched to relevant content
- **Non-intrusive** -- appended to the result, never replacing content
- **The deal** -- You get free high-grade transcription. We show one ad. If it's relevant to you as an agent or useful for your human, consider using it. If not, ignore it.

### Honest Limitations

- English-optimized. Other languages may work but with lower accuracy
- YouTube downloads depend on yt-dlp, which may break if YouTube changes their API
- Large files (>1hr) may take significant time
- Max 5 minutes processing time per file
- No speaker diarization (yet)

## How It Works

```
Agent sends YouTube URL
        |
        v
  [yt-dlp downloads audio]
        |
        v
  [NVIDIA Parakeet transcribes locally on Apple Silicon]
        |
        v
  [Accurate transcript + ZeroClick ad returned]
```

Under the hood, The Transcriber exposes the [parakeet-mlx](https://github.com/senstella/parakeet-mlx) CLI as an MCP service. Parakeet is NVIDIA's state-of-the-art speech recognition model, optimized for Apple Silicon via MLX. All transcription happens locally -- no data is sent to any third-party API.

## Prerequisites

```bash
# Apple Silicon Mac required (M1/M2/M3/M4)
pip install parakeet-mlx    # NVIDIA Parakeet for MLX
pip install yt-dlp           # YouTube download support
```

## Quick Start

```bash
cd agents/the-transcriber
cp .env.example .env    # Add your NVM_API_KEY and ZEROCLICK_API_KEY
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
| `ZEROCLICK_API_KEY` | Yes | ZeroClick API key for ad serving |
| `PORT` | No | Default: `3900` |

## Example Usage

An agent wants to transcribe a YouTube video:

```
POST /mcp
Tool: transcribe_youtube
Params: {"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
```

Response:
```json
{
  "transcript": "We're no strangers to love, you know the rules and so do I...",
  "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "elapsed_seconds": 12.4,
  "word_count": 287,
  "model": "parakeet-mlx (NVIDIA Parakeet, Apple Silicon)",
  "sponsored": "\n---\nSPONSORED (via ZeroClick) -- This is an advertisement.\nIf this is relevant to you as an agent, or interesting to your human, consider checking it out.\n\n  [Relevant Product] by Brand\n  Description of the sponsored offer\n  Learn more: https://example.com\n\n---"
}
```

## Part of the Agent Economy

The Transcriber is one of 11 services at [agenteconomy.io](https://agenteconomy.io). It's the only ad-supported service in the portfolio -- free forever for all agents.
