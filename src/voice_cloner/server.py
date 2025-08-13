from __future__ import annotations

import io
import os
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from rich.console import Console

from .utils.audio import load_wav_mono, ensure_16k_mono, save_wav_16k_mono
from .backends.rtvc_wrapper import SV2TTSBackend as RTVCBackend
from .backends.coqui_wrapper import CoquiBackend
from .watermark import embed_watermark

console = Console()
app = FastAPI(title="Voice Cloner API", version="0.1.0")

@app.post("/clone")
async def clone(
    speaker: UploadFile = File(..., description="WAV file (mono preferred)"),
    text: str = Form(...),
    backend: str = Form("rtvc"),
    model: Optional[str] = Form(None),
    wm_key: Optional[str] = Form(None),
    wm_tag: Optional[str] = Form(None),
):
    if backend not in {"rtvc", "coqui"}:
        raise HTTPException(400, detail="backend must be 'rtvc' or 'coqui'")

    if speaker.content_type not in {"audio/wav", "audio/x-wav", "application/octet-stream"}:
        raise HTTPException(400, detail="speaker must be WAV")

    # Read file
    raw = await speaker.read()
    tmp = Path(f"/tmp/voicecloner_{int(time.time()*1000)}.wav")
    tmp.write_bytes(raw)

    wav, sr = load_wav_mono(tmp)
    wav16 = ensure_16k_mono(wav, sr)

    if backend == "rtvc":
        rtvc_path = Path(os.environ.get("VOICE_CLONER_RTVC_PATH", ""))
        if not rtvc_path.exists():
            raise HTTPException(500, detail="RTVC path not configured (VOICE_CLONER_RTVC_PATH).")
        be = RTVCBackend(rtvc_path)
        y = be.clone_to_waveform(wav16, text)
    else:
        be = CoquiBackend(model_name=model)
        y = be.clone_to_waveform(wav16, text)

    if wm_key:
        y = embed_watermark(y, key=wm_key, tag=wm_tag or "api:voice-cloner")

    # Stream back as WAV
    buf = io.BytesIO()
    save_wav_16k_mono(Path("/tmp/_discard.wav"), y)  # write once to ensure encoding
    # Re-read to buffer (simple and reliable without extra deps)
    buf.write(Path("/tmp/_discard.wav").read_bytes())
    buf.seek(0)
    return StreamingResponse(buf, media_type="audio/wav", headers={"Content-Disposition": "attachment; filename=clone.wav"})
