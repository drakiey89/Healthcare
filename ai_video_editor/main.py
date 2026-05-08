import argparse
import logging
import sys

import transcriber
import llm_handler
import asset_manager
import video_processor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="AI Video Editor — transforms talking-head videos into social clips.")
    parser.add_argument("input_video", help="Path to the input video file")
    parser.add_argument("--output", default="output.mp4", help="Output filename (default: output.mp4)")
    args = parser.parse_args()

    # Stage 1 — Transcription
    logger.info("Stage 1: Transcription")
    try:
        audio_path = transcriber.extract_audio(args.input_video)
        transcript = transcriber.transcribe_audio(audio_path)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        sys.exit(1)

    # Stage 2 — Script Generation
    logger.info("Stage 2: Generating editing script via LLM")
    try:
        editing_script = llm_handler.generate_editing_script(transcript)
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        sys.exit(1)

    # Stage 3 — Asset Collection
    logger.info("Stage 3: Collecting assets")
    try:
        assets = {}
        for clip in editing_script.get("clips", []):
            keyword = clip.get("b_roll_keyword")
            if keyword and keyword not in assets:
                assets[f"broll_{keyword}"] = asset_manager.get_b_roll(keyword)

        music_mood = editing_script.get("music", {}).get("mood", "upbeat")
        assets["music"] = asset_manager.get_music(music_mood)

        for clip in editing_script.get("clips", []):
            sfx_query = clip.get("sound_effect")
            if sfx_query and f"sfx_{sfx_query}" not in assets:
                assets[f"sfx_{sfx_query}"] = asset_manager.get_sfx(sfx_query)
    except Exception as e:
        logger.error(f"Asset collection failed: {e}")
        sys.exit(1)

    # Stage 4 — Rendering
    logger.info("Stage 4: Rendering video")
    try:
        video_processor.render_video(args.input_video, editing_script, assets, args.output)
        logger.info(f"Done! Output saved to {args.output}")
    except Exception as e:
        logger.error(f"Rendering failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
