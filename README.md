# Voice Cloning (SV2TTS) — Pro Starter

**Production-style** starter for voice cloning with **switchable backends** and an **API server**:
- Backends: **RTVC** (CorentinJ) and **Coqui TTS (multi-speaker)** via thin wrappers
- **FastAPI server** with `/clone` endpoint (multipart: `speaker` WAV + `text` + `backend`)
- **Soft watermark** (spread-spectrum) for tagging outputs (embed/detect)
- CLI, tests, Docker, CI, pre-commit, and a minimal notebook

> ⚠️ **Ethics & Consent**
> - Clone **only your own voice** or voices with **explicit written consent**.
> - Clearly label synthetic audio.
> - Follow local laws and platform policies.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: py -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

### Connect a backend
**RTVC (recommended classic)**
```bash
git clone https://github.com/CorentinJ/Real-Time-Voice-Cloning.git ~/rtvc
export VOICE_CLONER_RTVC_PATH=~/rtvc
```

**Coqui TTS (multi-speaker)**
```bash
pip install TTS                       # coqui-ai TTS
# Choose a multi-speaker model name, e.g. "tts_models/en/vctk/vits"
```

## CLI
```bash
python -m voice_cloner.cli clone   --backend rtvc   --speaker assets/samples/spk.wav   --text "Hello from a consented voice clone."   --out out.wav   --wm-key "secret123"   --wm-tag "demo:soheil:2025-08-13"
# or Coqui
python -m voice_cloner.cli clone   --backend coqui   --model "tts_models/en/vctk/vits"   --speaker assets/samples/spk.wav   --text "Hello from Coqui backend."   --out out.wav
```

## API Server
```bash
uvicorn voice_cloner.server:app --host 0.0.0.0 --port 8000
```
**POST** `/clone` (multipart/form-data):
- `speaker`: WAV file (mono recommended)
- `text`: string
- `backend`: `rtvc` or `coqui`
- `model` (optional): for coqui, e.g., `tts_models/en/vctk/vits`
- `wm_key` (optional): watermark secret
- `wm_tag` (optional): watermark tag string

Response: WAV audio stream.

## Notebook
See: `notebooks/voice_clone_demo.ipynb`

## Tests
```bash
pytest -q
```

## Structure
```
src/voice_cloner/
  cli.py
  server.py
  watermark.py
  backends/
    rtvc_wrapper.py
    coqui_wrapper.py
  utils/
    audio.py
tests/
  test_cli.py
  test_watermark.py
  test_server_import.py
assets/
  samples/          # put your own sample
...
```
