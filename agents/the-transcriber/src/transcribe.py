"""Transcription engine -- runs NVIDIA Parakeet locally on Apple Silicon via parakeet-mlx.

Assembly AI for AI agents, except free.
"""
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

# Lazy-load the model on first use
_model = None


def _get_model():
    """Load and cache the Parakeet model."""
    global _model
    if _model is None:
        from parakeet_mlx import from_pretrained
        _model = from_pretrained("mlx-community/parakeet-tdt-0.6b-v2")
    return _model


def is_parakeet_available() -> bool:
    """Check if parakeet-mlx is installed."""
    try:
        import parakeet_mlx  # noqa: F401
        return True
    except ImportError:
        return False


def transcribe_file(audio_path: str) -> dict:
    """Transcribe an audio file using parakeet-mlx (local Apple Silicon model).

    Returns dict with transcript text, duration, and metadata.
    """
    path = Path(audio_path)
    if not path.exists():
        return {"error": f"File not found: {audio_path}"}

    if not is_parakeet_available():
        return {"error": "parakeet-mlx not installed. Install with: pip install parakeet-mlx"}

    start = time.time()

    try:
        model = _get_model()
        result = model.transcribe(path)
        elapsed = time.time() - start

        transcript = result.text.strip()
        return {
            "transcript": transcript,
            "source": str(path),
            "elapsed_seconds": round(elapsed, 2),
            "word_count": len(transcript.split()),
            "char_count": len(transcript),
            "model": "parakeet-mlx (NVIDIA Parakeet, Apple Silicon)",
        }

    except Exception as e:
        elapsed = time.time() - start
        return {
            "error": f"Transcription failed: {str(e)[:200]}",
            "elapsed_seconds": round(elapsed, 2),
        }


def download_youtube_audio(url: str) -> str | None:
    """Download audio from a YouTube URL using yt-dlp.

    Returns the path to the downloaded audio file, or None on failure.
    """
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        # Try via poetry venv
        try:
            import yt_dlp as _  # noqa: F401
            yt_dlp = "yt-dlp"
        except ImportError:
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
    if not is_parakeet_available():
        return {"error": "parakeet-mlx not installed. Install with: pip install parakeet-mlx"}

    # Download audio
    download_start = time.time()
    audio_path = download_youtube_audio(url)
    download_time = time.time() - download_start

    if not audio_path:
        return {"error": f"Failed to download audio from: {url}. Ensure yt-dlp is installed."}

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
        "service": "The Transcriber -- Assembly AI for AI Agents, Except Free",
        "model": "parakeet-mlx (NVIDIA Parakeet on Apple Silicon)",
        "compute": "Local Apple Silicon -- real ML compute, not an API wrapper",
        "parakeet_installed": has_parakeet,
        "yt_dlp_installed": has_ytdlp,
        "supported_inputs": [
            "YouTube URLs (auto-download + transcribe)",
            "Audio files (wav, mp3, m4a, flac, ogg)",
            "Video files (mp4, mkv, webm -- audio extracted)",
        ],
        "supported_outputs": ["Plain text transcript"],
        "pricing": "FREE (0 credits). Ad-supported via ZeroClick.",
        "max_duration": "5 minutes processing time per file",
        "limitations": [
            "English-optimized (Parakeet is primarily English)",
            "Processing time depends on audio length",
            "No speaker diarization (yet)",
        ],
    }
