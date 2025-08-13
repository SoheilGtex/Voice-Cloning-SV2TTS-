from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

class SV2TTSBackend:
    """A thin wrapper that imports RTVC modules dynamically via sys.path."""

    def __init__(self, rtvc_root: Path):
        self.rtvc_root = Path(rtvc_root).resolve()
        sys.path.insert(0, str(self.rtvc_root))
        try:
            from encoder import inference as encoder
            from synthesizer.inference import Synthesizer
            from vocoder import inference as vocoder
        except Exception as e:
            raise RuntimeError(f"Failed to import RTVC from {self.rtvc_root}: {e}")
        self._encoder = encoder
        self._Synth = Synthesizer
        self._vocoder = vocoder

    def clone_to_waveform(self, ref_wave_16k: np.ndarray, text: str) -> np.ndarray:
        embed = self._encoder.embed_utterance(ref_wave_16k)
        synth = self._Synth(self.rtvc_root / "synthesizer/saved_models/pretrained")
        specs = synth.synthesize_spectrograms([text], [embed])
        spec = specs[0]
        self._vocoder.load_model(self.rtvc_root / "vocoder/saved_models/pretrained")
        wav = self._vocoder.infer_waveform(spec)
        return wav.astype(np.float32)
