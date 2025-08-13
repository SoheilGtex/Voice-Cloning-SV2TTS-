from __future__ import annotations

from typing import Optional
from pathlib import Path
import numpy as np

class CoquiBackend:
    """
    Minimal wrapper around Coqui TTS API.
    Requires: pip install TTS
    For multi-speaker English try: "tts_models/en/vctk/vits"
    """
    def __init__(self, model_name: Optional[str] = None):
        try:
            from TTS.api import TTS
        except Exception as e:
            raise RuntimeError("Coqui TTS not installed. `pip install TTS`") from e
        self.model_name = model_name or "tts_models/en/vctk/vits"
        self.tts = TTS(self.model_name)

    def clone_to_waveform(self, ref_wave_16k: np.ndarray, text: str) -> np.ndarray:
        """
        Coqui TTS multi-speaker models usually take a speaker embedding or a reference wav path.
        Here we pass the raw reference waveform if supported; otherwise users may save it and pass a path.
        """
        try:
            # Some models accept a numpy array via speaker_wav
            y = self.tts.tts(text=text, speaker_wav=ref_wave_16k, sample_rate=16000)
        except Exception:
            # Fallback: save temp ref and pass path
            import soundfile as sf, tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                sf.write(f.name, ref_wave_16k, 16000, subtype="PCM_16")
                y = self.tts.tts(text=text, speaker_wav=f.name, sample_rate=16000)
        y = np.asarray(y, dtype=np.float32).squeeze()
        return y
