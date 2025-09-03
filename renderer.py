# renderer.py
import os, re, shutil, subprocess, time, uuid
from typing import Literal
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# default font inside the repo
DEFAULT_FONT = os.getenv("FONT_FILE", "fonts/IBMPlexSansArabic-Bold.ttf")
AR_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

def _looks_arabic(s: str) -> bool:
    return bool(AR_RE.search(s))

def _shape_ar(text: str) -> str:
    # connect Arabic letters correctly
    return get_display(arabic_reshaper.reshape(text))

def _measure_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> float:
    # robust width across Pillow versions
    if hasattr(font, "getlength"):
        try: return font.getlength(text)
        except: pass
    if hasattr(draw, "textlength"):
        try: return draw.textlength(text, font=font)
        except: pass
    bbox = draw.textbbox((0,0), text, font=font)
    return bbox[2]-bbox[0]

def render_title_card(
    text: str,
    out_dir: str = "out",
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
    total_dur: float = 5.0,
    letter_delay: float = 0.06,
    fade_dur: float = 0.35,
    rise_px: int = 40,
    x_slide_px: int = 30,
    font_size: int = 96,
    font_file: str = DEFAULT_FONT,
    direction: Literal["auto","ltr","rtl"] = "auto",
    bg=(0,0,0,255),
    fill=(255,255,255,255),
    shadow=(0,0,0,110),
    stroke_w: int = 0,
    stroke_fill=(0,0,0,160),
) -> str:
    """Renders a letter-by-letter animated title card; returns the MP4 filename created in out_dir."""

    # decide direction
    is_ar = _looks_arabic(text)
    dir_mode = ("rtl" if is_ar else "ltr") if direction == "auto" else direction

    # shape Arabic to connect letters
    vis_text = _shape_ar(text) if is_ar else text

    # workspace
    os.makedirs(out_dir, exist_ok=True)
    job_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    frames_dir = os.path.join(out_dir, f"frames_{job_id}")
    os.makedirs(frames_dir, exist_ok=True)

    # font & scene
    font = ImageFont.truetype(font_file, font_size)
    base = Image.new("RGBA", (width, height))
    drw = ImageDraw.Draw(base)
    chars = list(vis_text)
    n = len(chars)

    # timings
    if dir_mode == "rtl":
        starts = [(n - 1 - i) * letter_delay for i in range(n)]
    else:
        starts = [i * letter_delay for i in range(n)]
    min_total = max(starts) + fade_dur + 0.6
    duration = max(total_dur, min_total)
    total_frames = round(duration * fps)

    # positions
    advances = [_measure_w(drw, "".join(chars[:i]), font) for i in range(n)]
    total_w = _measure_w(drw, "".join(chars), font)
    base_x = (width - total_w) / 2.0
    baseline_y = height/2.0 - font_size/2.8
    x_sign = +1 if dir_mode == "ltr" else -1

    def ease_out_cubic(t: float) -> float:
        return 1 - (1 - t) ** 3

    # render frames
    for f in range(total_frames):
        t = f / fps
        frame = Image.new("RGBA", (width, height), bg)
        draw = ImageDraw.Draw(frame)

        for i, ch in enumerate(chars):
            t0 = starts[i]
            local = (t - t0) / fade_dur
            if local <= 0:
                continue
            prog = min(max(local, 0.0), 1.0)
            e = ease_out_cubic(prog)

            alpha = int(255 * e)
            y_off = int(rise_px * (1 - e))
            x = int(base_x + advances[i] + x_sign * x_slide_px * (1 - e))
            y = int(baseline_y + y_off)

            # shadow
            if shadow[3] > 0:
                draw.text((x+2, y+2), ch, font=font,
                          fill=(shadow[0],shadow[1],shadow[2], int(shadow[3]*(alpha/255))))

            # glyph
            draw.text((x, y), ch, font=font,
                      fill=(fill[0],fill[1],fill[2], alpha),
                      stroke_width=stroke_w,
                      stroke_fill=(stroke_fill[0],stroke_fill[1],stroke_fill[2], int(stroke_fill[3]*(alpha/255))))

        frame.save(os.path.join(frames_dir, f"{f:05d}.png"))

    # encode to mp4 (requires ffmpeg installed)
    mp4_name = f"card_{job_id}.mp4"
    mp4_path = os.path.join(out_dir, mp4_name)
    subprocess.run([
        "ffmpeg","-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "%05d.png"),
        "-pix_fmt","yuv420p","-c:v","libx264","-preset","medium","-crf","18",
        "-movflags","+faststart", mp4_path
    ], check=True)

    shutil.rmtree(frames_dir, ignore_errors=True)
    return mp4_name


    # --- PNG renderer (single image) ---------------------------------------------
# --- PNG renderer (single image, Arabic-safe) -------------------------------
# --- PNG renderer (single image, Arabic-safe) -------------------------------
def render_card_png(...):
    os.makedirs(out_dir, exist_ok=True)

    # Check RAQM availability
    has_raqm = hasattr(ImageFont, "LAYOUT_RAQM")

    is_ar = _looks_arabic(text)
    use_rtl = (direction == "rtl") or (direction == "auto" and is_ar)

    # Choose ONE shaping path
    if has_raqm:
        # Path A: RAQM does shaping/kerning/RTL
        vis_text = text  # raw
        font = ImageFont.truetype(
            font_file, font_size, layout_engine=ImageFont.LAYOUT_RAQM
        )
        dir_kwargs = {"direction": ("rtl" if use_rtl else "ltr")}
    else:
        # Path B: fallback to manual shaping; then draw as-is
        vis_text = _shape_ar(text) if is_ar else text
        font = ImageFont.truetype(font_file, font_size)
        dir_kwargs = {}  # don't pass direction without RAQM

    # --- measure & center ---
    img = Image.new("RGBA", (width, height), bg)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), vis_text, font=font, **dir_kwargs)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    while text_w > (width - 2 * padding) and font_size > 24:
        font_size = int(font_size * 0.9)
        if has_raqm:
            font = ImageFont.truetype(font_file, font_size, layout_engine=ImageFont.LAYOUT_RAQM)
        else:
            font = ImageFont.truetype(font_file, font_size)
        bbox = draw.textbbox((0, 0), vis_text, font=font, **dir_kwargs)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x = (width - text_w) // 2
    y = (height - text_h) // 2

    # Shadow then text
    if shadow[3] > 0:
        draw.text((x + 2, y + 2), vis_text, font=font,
                  fill=(shadow[0], shadow[1], shadow[2], shadow[3]),
                  **dir_kwargs)
    draw.text((x, y), vis_text, font=font, fill=fill, **dir_kwargs)

    name = f"card_{int(time.time())}-{uuid.uuid4().hex[:8]}.png"
    img.save(os.path.join(out_dir, name), "PNG")
    return name
