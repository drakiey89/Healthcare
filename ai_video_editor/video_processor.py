import os
import logging
import textwrap

logger = logging.getLogger(__name__)

_TEMP_CAPTIONS: list[str] = []


def create_caption_image(text: str, style: str, video_width: int, video_height: int) -> str:
    """Render a styled caption as a PNG and return the file path."""
    from PIL import Image, ImageDraw, ImageFont

    font_size = max(24, video_width // 30)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    max_chars = max(10, video_width // (font_size // 2))
    wrapped = "\n".join(textwrap.wrap(text, max_chars))

    img = Image.new("RGBA", (video_width, video_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if style == "modern_lower_third":
        bar_h = text_h + 40
        bar_y = video_height - bar_h - 20
        draw.rectangle([0, bar_y, video_width, bar_y + bar_h], fill=(0, 0, 0, 180))
        draw.text(((video_width - text_w) / 2, bar_y + 20), wrapped, font=font, fill=(255, 255, 255, 255))

    elif style == "pop_up_caption":
        pad = 20
        x0 = (video_width - text_w) / 2 - pad
        y0 = video_height * 0.75 - pad
        draw.rounded_rectangle([x0, y0, x0 + text_w + pad * 2, y0 + text_h + pad * 2], radius=15, fill=(0, 0, 0, 200))
        draw.text((x0 + pad, y0 + pad), wrapped, font=font, fill=(255, 255, 255, 255))

    else:  # minimalist_overlay / kinetic_type
        cx = (video_width - text_w) / 2
        cy = video_height * 0.8
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw.text((cx + dx, cy + dy), wrapped, font=font, fill=(0, 0, 0, 200))
        draw.text((cx, cy), wrapped, font=font, fill=(255, 255, 255, 255))

    dest = f"/tmp/caption_{abs(hash(text))}_{style}.png"
    img.save(dest)
    _TEMP_CAPTIONS.append(dest)
    return dest


def render_video(input_video: str, editing_script: dict, assets: dict, output_path: str) -> None:
    """Composite the input video with captions, B-roll, and audio from the editing script."""
    from moviepy.editor import (
        VideoFileClip,
        ImageClip,
        CompositeVideoClip,
        AudioFileClip,
        concatenate_videoclips,
    )

    base = VideoFileClip(input_video)
    w, h = base.size
    scenes = []

    for clip_def in editing_script.get("clips", []):
        start = clip_def.get("start", 0)
        end = clip_def.get("end", base.duration)
        end = min(end, base.duration)

        broll_key = clip_def.get("b_roll_keyword")
        broll_path = assets.get(f"broll_{broll_key}") if broll_key else None

        if broll_path and os.path.exists(broll_path):
            scene = VideoFileClip(broll_path).subclip(0, end - start).resize((w, h))
        else:
            scene = base.subclip(start, end)

        layers = [scene]

        caption_text = clip_def.get("caption")
        if caption_text:
            style = clip_def.get("caption_style", "minimalist_overlay")
            cap_img = create_caption_image(caption_text, style, w, h)
            cap_clip = ImageClip(cap_img).set_duration(scene.duration).set_position(("center", "bottom"))
            layers.append(cap_clip)

        scenes.append(CompositeVideoClip(layers))

    if not scenes:
        scenes = [base]

    final = concatenate_videoclips(scenes, method="compose", padding=-0.5)

    music_path = assets.get("music")
    if music_path and os.path.exists(music_path):
        music_vol = editing_script.get("music", {}).get("volume", 0.1)
        music = AudioFileClip(music_path).volumex(music_vol).subclip(0, final.duration)
        from moviepy.audio.AudioClip import CompositeAudioClip
        original_audio = final.audio
        if original_audio:
            final = final.set_audio(CompositeAudioClip([original_audio, music]))
        else:
            final = final.set_audio(music)

    final.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

    for path in _TEMP_CAPTIONS:
        if os.path.exists(path):
            os.remove(path)
    _TEMP_CAPTIONS.clear()
    logger.info(f"Video written to {output_path}")
