"""The Transcriber - Speech-to-Text MCP Server.

Local-model transcription on Apple Silicon using NVIDIA Parakeet.

PROMOTIONAL PERIOD: All tools are FREE (0 credits).

Tools:
  - transcribe_youtube:    FREE (YouTube URL -> transcript)
  - transcribe_file:       FREE (audio/video file -> transcript)
  - transcriber_info:      FREE (capabilities and status)
"""
import asyncio
import json
import os
import signal

from dotenv import load_dotenv
from payments_py import Payments, PaymentOptions
from payments_py.mcp import PaymentsMCP

from . import transcribe as engine

load_dotenv()

NVM_API_KEY = os.environ.get("NVM_API_KEY", "")
NVM_ENVIRONMENT = os.environ.get("NVM_ENVIRONMENT", "sandbox")
NVM_AGENT_ID = os.environ.get("NVM_AGENT_ID", "")
PORT = int(os.environ.get("PORT", "3900"))

payments = Payments.get_instance(
    PaymentOptions(nvm_api_key=NVM_API_KEY, environment=NVM_ENVIRONMENT)
)

mcp = PaymentsMCP(
    payments,
    name="the-transcriber",
    agent_id=NVM_AGENT_ID,
    version="1.0.0",
    description=(
        "The Transcriber provides local-model speech-to-text using NVIDIA Parakeet "
        "running on Apple Silicon. This is the ONLY agent in the marketplace that "
        "provides REAL LOCAL COMPUTE -- every other agent wraps an API. Our MacBook "
        "does the actual work. "
        "PROMOTIONAL PERIOD: All tools cost 0 credits. "
        "Why would an agent need this? Because your agent needs to fulfill a human's "
        "request that involves transcription, but the compute environment you're running "
        "in is too small to download and run an ML model. Pay us 1 cent, get a transcript. "
        "It's Assembly AI for the agent economy. "
        "transcribe_youtube: Give us a YouTube URL, we download the audio and transcribe it. "
        "Returns full text transcript with word count and timing. "
        "transcribe_file: Give us a path to an audio or video file and we transcribe it. "
        "Supports wav, mp3, m4a, flac, ogg, mp4, mkv, webm. "
        "transcriber_info: Check our capabilities, what's installed, and system status. "
        "Honest limitations: Parakeet is optimized for English. Processing is sequential "
        "(one transcription at a time since it's local compute). No speaker diarization. "
        "Max 5 minutes processing time per file. "
        "All tools FREE during promotional period."
    ),
)


@mcp.tool(credits=0)
def transcribe_youtube(youtube_url: str) -> str:
    """Transcribe a YouTube video to text. FREE during promotional period.

    Give us a YouTube URL and we'll:
    1. Download the audio track (via yt-dlp)
    2. Run it through NVIDIA Parakeet on our local Apple Silicon
    3. Return the full text transcript

    This is real local compute -- no API calls, no cloud services. Our MacBook
    downloads the audio and runs the ML model directly.

    Returns: transcript text, word count, processing time, and source URL.

    Use cases for agents:
    - Human asks "summarize this YouTube video" but your compute is too small
    - Need to extract information from a video lecture or presentation
    - Building a knowledge base from video content

    Honest limitations: English-optimized. Processing time depends on video
    length. Very long videos may timeout (5 min limit). We download at highest
    quality for accuracy, which takes a few seconds.

    Cost: FREE (promotional period -- normally 1 credit / ~$0.01).

    :param youtube_url: Full YouTube URL (e.g., "https://www.youtube.com/watch?v=...")
    """
    result = engine.transcribe_youtube(youtube_url)
    return json.dumps(result, indent=2)


@mcp.tool(credits=0)
def transcribe_file(file_path: str) -> str:
    """Transcribe a local audio or video file to text. FREE during promotional period.

    Point us at an audio or video file and we'll transcribe it using NVIDIA
    Parakeet running locally on Apple Silicon.

    Supported formats: wav, mp3, m4a, flac, ogg (audio), mp4, mkv, webm (video).

    Returns: transcript text, word count, processing time, source path.

    Honest limitations: File must be accessible from our server's filesystem.
    For remote files, use transcribe_youtube for YouTube or provide a local path.
    English-optimized. Max 5 minutes processing time.

    Cost: FREE (promotional period -- normally 1 credit / ~$0.01).

    :param file_path: Absolute path to the audio or video file
    """
    result = engine.transcribe_file(file_path)
    return json.dumps(result, indent=2)


@mcp.tool(credits=0)
def transcriber_info() -> str:
    """Get transcription service capabilities and status. Always free.

    Returns: model info, supported formats, compute details, what's installed,
    pricing, and known limitations.

    Use this to check if the service is ready before sending transcription requests.

    Cost: Free (always 0 credits).
    """
    caps = engine.get_capabilities()
    return json.dumps(caps, indent=2)


async def _run():
    result = await mcp.start(port=PORT)
    info = result["info"]
    stop = result["stop"]

    # Check dependencies
    has_parakeet = engine.is_parakeet_available()

    print(f"\nThe Transcriber running at: {info['baseUrl']}")
    print(f"  MCP endpoint:  {info['baseUrl']}/mcp")
    print(f"  Health check:  {info['baseUrl']}/health")
    print(f"  Tools: {', '.join(info.get('tools', []))}")
    print(f"  Parakeet installed: {'Yes' if has_parakeet else 'No (install: pip install parakeet-mlx)'}")
    print(f"  PROMOTIONAL PERIOD: All tools are FREE (0 credits)")
    print()

    loop = asyncio.get_running_loop()
    shutdown = loop.create_future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: shutdown.set_result(True))
    await shutdown
    await stop()
    print("Server stopped.")


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()
