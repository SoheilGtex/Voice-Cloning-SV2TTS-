from __future__ import annotations

import numpy as np
from typing import Optional

def _pn_sequence(length: int, key: str) -> np.ndarray:
    # Simple deterministic pseudo-noise based on key (not cryptographic).
    seed = abs(hash(key)) % (2**32 - 1)
    rng = np.random.default_rng(seed)
    return rng.standard_normal(length).astype("float32")

def embed_watermark(y: np.ndarray, key: str, tag: Optional[str] = None, strength_db: float = -35.0) -> np.ndarray:
    """
    Add a spread-spectrum watermark to the waveform at ~-35 dB.
    - key: secret string
    - tag: optional string mixed into key
    """
    if y.ndim != 1:
        y = y.squeeze()
    mix_key = f"{key}|{tag}" if tag else key
    pn = _pn_sequence(len(y), mix_key)
    # Convert dB to linear gain
    gain = 10 ** (strength_db / 20.0)
    y_wm = (y + gain * pn).astype("float32")
    # soft limiter
    mx = max(1e-9, float(np.max(np.abs(y_wm))))
    if mx > 1.0:
        y_wm = y_wm / mx * 0.98
    return y_wm

def detect_watermark(y: np.ndarray, key: str, tag: Optional[str] = None) -> float:
    """
    Correlation score with the PN sequence (higher ⇒ more likely watermarked).
    Not robust to heavy post-processing; intended as lightweight tagging.
    """
    if y.ndim != 1:
        y = y.squeeze()
    mix_key = f"{key}|{tag}" if tag else key
    pn = _pn_sequence(len(y), mix_key)
    # normalized correlation
    num = float(np.dot(y, pn))
    den = float(np.linalg.norm(y) * np.linalg.norm(pn) + 1e-9)
    return num / den
