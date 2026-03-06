"""Transcription engine — runs Parakeet locally on Apple Silicon for fast speech-to-text.

This is the only agent in the marketplace providing REAL LOCAL COMPUTE.
Every other agent wraps an API. We run the model on our MacBook.
"""
import os
import json
import time
import shutil
import tempfile
import subprocess
from pathlib import Path


def is_parakeet_available() -> bool:
    """Check if parakeet-mlx is installed and available."""
    return shutil.which("parakeet") is not None


def transcribe_file(audio_path: str) -> dict:
    """Transcribe an audio file using parakeet-mlx (local Apple Silicon model).

    Returns dict with transcript text, duration, and metadata.
    """
    path = Path(audio_path)
    if not path.exists():
        return {"error": f"File not found: {audio_path}"}

    start = time.time()

    try:
        result = subprocess.run(
            ["parakeet", str(path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max
        )

        elapsed = time.time() - start

        if result.returncode != 0:
            return {
                "error": f"Parakeet failed: {result.stderr[:500]}",
                "elapsed_seconds": round(elapsed, 2),
            }

        transcript = result.stdout.strip()
        return {
            "transcript": transcript,
            "source": str(path),
            "elapsed_seconds": round(elapsed, 2),
            "word_count": len(transcript.split()),
            "char_count": len(transcript),
            "model": "parakeet-mlx (NVIDIA Parakeet, Apple Silicon)",
        }

    except subprocess.TimeoutExpired:
        return {"error": "Transcription timed out (>5 minutes)"}
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)[:200]}"}


def download_youtube_audio(url: str) -> str | None:
    """Download audio from a YouTube URL using yt-dlp.

    Returns the path to the downloaded audio file, or None on failure.
    """
    if not shutil.which("yt-dlp"):
        return None

    tmpdir = tempfile.mkdtemp(prefix="transcriber_")
    output_path = os.path.join(tmpdir, "audio.%(ext)s")

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "wav",
                "--audio-quality", "0",
                "--output", output_path,
                "--no-playlist",
                "--quiet",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return None

        # Find the downloaded file
        for f in os.listdir(tmpdir):
            if f.startswith("audio"):
                return os.path.join(tmpdir, f)

        return None
    except Exception:
        return None


def transcribe_youtube(url: str) -> dict:
    """Download and transcribe a YouTube video."""
    if not shutil.which("yt-dlp"):
        return {"error": "yt-dlp not installed. Install with: pip install yt-dlp"}

    if not is_parakeet_available():
        return {"error": "parakeet-mlx not installed. Install with: pip install parakeet-mlx"}

    # Download audio
    download_start = time.time()
    audio_path = download_youtube_audio(url)
    download_time = time.time() - download_start

    if not audio_path:
        return {"error": f"Failed to download audio from: {url}"}

    # Transcribe
    result = transcribe_file(audio_path)

    # Cleanup
    try:
        tmpdir = os.path.dirname(audio_path)
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass

    if "error" not in result:
        result["source_url"] = url
        result["download_seconds"] = round(download_time, 2)
        result["total_seconds"] = round(
            download_time + result.get("elapsed_seconds", 0), 2
        )

    return result


def get_capabilities() -> dict:
    """Report what this transcription service can do."""
    has_parakeet = is_parakeet_available()
    has_ytdlp = shutil.which("yt-dlp") is not None

    return {
        "service": "The Transcriber",
        "model": "parakeet-mlx (NVIDIA Parakeet on Apple Silicon)",
        "compute": "Local MacBook -- real compute, not an API wrapper",
        "parakeet_installed": has_parakeet,
        "yt_dlp_installed": has_ytdlp,
        "supported_inputs": [
            "YouTube URLs (auto-download + transcribe)",
            "Audio files (wav, mp3, m4a, flac, ogg)",
            "Video files (mp4, mkv, webm -- audio extracted)",
        ],
        "supported_outputs": ["Plain text transcript"],
        "pricing": "1 credit per transcription (~$0.01)",
        "max_duration": "5 minutes processing time per file",
        "limitations": [
            "English-optimized (Parakeet is primarily English)",
            "Processing time depends on audio length",
            "Local compute means one transcription at a time",
            "No speaker diarization (yet)",
        ],
    }
