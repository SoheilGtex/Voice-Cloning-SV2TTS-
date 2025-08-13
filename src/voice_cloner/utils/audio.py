from __future__ import annotations

from pathlib import Path
import numpy as np
import soundfile as sf
import librosa

TARGET_SR = 16000

def load_wav_mono(path: Path):
    y, sr = sf.read(str(path))
    if y.ndim == 2:
        y = y.mean(axis=1)
    y = y.astype("float32")
    return y, sr

def ensure_16k_mono(y: np.ndarray, sr: int) -> np.ndarray:
    if sr != TARGET_SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SR)
    if y.ndim != 1:
        y = y.squeeze()
    mx = max(1e-9, float(np.max(np.abs(y))))
    y = y / mx * 0.97
    return y.astype("float32")

def save_wav_16k_mono(path: Path, y: np.ndarray):
    sf.write(str(path), y, TARGET_SR, subtype="PCM_16")
