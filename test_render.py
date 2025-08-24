# test_render.py
from renderer import render_title_card

mp4 = render_title_card(
    text="صميم ستوديوز تقدم",   # try English: "SAMIM STUDIOS PRESENTS"
    direction="auto",            # auto → RTL for Arabic, LTR for English
    font_file="fonts/IBMPlexSansArabic-Bold.ttf",
    total_dur=6.0,               # a bit longer
    letter_delay=0.08,
    fade_dur=0.45,
    rise_px=30,
    x_slide_px=24,
    font_size=100,
)
print("OK → out/" + mp4)
