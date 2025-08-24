# main.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal, Optional
from renderer import render_title_card

OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)

app = FastAPI(title="AI Scenes Render API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for local testing; we can lock later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=OUT_DIR), name="static")

class CardReq(BaseModel):
    text: str = Field(..., min_length=1, max_length=120)
    direction: Literal["auto","ltr","rtl"] = "auto"
    width: int = 1920
    height: int = 1080
    fps: int = 24
    total_dur: float = 5.0
    letter_delay: float = 0.06
    fade_dur: float = 0.35
    rise_px: int = 40
    x_slide_px: int = 30
    font_size: int = 96
    font_file: Optional[str] = "fonts/IBMPlexSansArabic-Bold.ttf"

@app.get("/")
def root():
    return {"ok": True, "hint": "POST /render/card"}

@app.post("/render/card")
def render_card(req: CardReq, request: Request):
    try:
        mp4_name = render_title_card(
            text=req.text,
            out_dir=OUT_DIR,
            width=req.width, height=req.height, fps=req.fps,
            total_dur=req.total_dur, letter_delay=req.letter_delay,
            fade_dur=req.fade_dur, rise_px=req.rise_px, x_slide_px=req.x_slide_px,
            font_size=req.font_size, font_file=req.font_file or "fonts/IBMPlexSansArabic-Bold.ttf",
            direction=req.direction,
        )
        base = str(request.base_url).rstrip("/")
        url = f"{base}/static/{mp4_name}"
        return {"status":"ok","url":url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
