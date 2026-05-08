import os
import logging

logger = logging.getLogger(__name__)


def extract_audio(video_path: str) -> str:
    """Extract audio from a video file and save as MP3."""
    from moviepy.editor import VideoFileClip

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    audio_path = os.path.splitext(video_path)[0] + "_audio.mp3"
    logger.info(f"Extracting audio to {audio_path}")

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, logger=None)
    clip.close()

    return audio_path


def transcribe_audio(audio_path: str) -> list[dict]:
    """Transcribe audio with word-level timestamps using Faster Whisper.

    Returns a list of {"word": str, "start": float, "end": float} dicts.
    Swap "tiny" for "large-v3" for higher accuracy.
    """
    from faster_whisper import WhisperModel

    logger.info(f"Transcribing {audio_path}")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, word_timestamps=True)

    words = []
    for segment in segments:
        if segment.words:
            for word in segment.words:
                words.append({"word": word.word.strip(), "start": word.start, "end": word.end})

    os.remove(audio_path)
    logger.info(f"Transcription complete: {len(words)} words")
    return words
