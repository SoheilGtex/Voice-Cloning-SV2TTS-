from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .utils.audio import load_wav_mono, save_wav_16k_mono, ensure_16k_mono
from .backends.rtvc_wrapper import SV2TTSBackend as RTVCBackend
from .backends.coqui_wrapper import CoquiBackend
from .watermark import embed_watermark

console = Console()

@click.group()
def cli():
    """Voice Cloner CLI"""
    pass

@cli.command(help="Clone a voice from a speaker reference and synthesize target text.")
@click.option("--backend", type=click.Choice(["rtvc", "coqui"]), default="rtvc")
@click.option("--speaker", type=click.Path(exists=True, dir_okay=False), required=True, help="Path to speaker WAV (mono; 16kHz recommended).")
@click.option("--text", type=str, required=True, help="Text to synthesize.")
@click.option("--out", type=click.Path(dir_okay=False), default="out.wav", help="Output WAV path.")
@click.option("--rtvc", type=click.Path(exists=True, file_okay=False), default=None, help="Path to RTVC repo (fallback to VOICE_CLONER_RTVC_PATH).")
@click.option("--model", type=str, default=None, help="Coqui model name (e.g., tts_models/en/vctk/vits).")
@click.option("--wm-key", type=str, default=None, help="Watermark key (secret). If not set, uses WATERMARK_KEY env if available.")
@click.option("--wm-tag", type=str, default=None, help="Optional watermark tag string.")
def clone(backend: str, speaker: str, text: str, out: str, rtvc: Optional[str], model: Optional[str], wm_key: Optional[str], wm_tag: Optional[str]):
    console.print("[bold yellow]Use with consent only. Label synthetic audio. Follow local laws.[/]")

    wav, sr = load_wav_mono(Path(speaker))
    wav16 = ensure_16k_mono(wav, sr)

    if backend == "rtvc":
        rtvc_path = Path(rtvc) if rtvc else Path(os.environ.get("VOICE_CLONER_RTVC_PATH", ""))
        if not rtvc_path.exists():
            console.print("[red]RTVC path not found. Set --rtvc or VOICE_CLONER_RTVC_PATH.[/]")
            raise SystemExit(2)
        be = RTVCBackend(rtvc_path)
        y = be.clone_to_waveform(wav16, text)
    else:
        be = CoquiBackend(model_name=model)
        y = be.clone_to_waveform(wav16, text)

    # Optional watermarking
    key = wm_key or os.environ.get("WATERMARK_KEY")
    if key:
        y = embed_watermark(y, key=key, tag=wm_tag or "voice-cloner")

    save_wav_16k_mono(Path(out), y)
    console.print(f"[bold green]Done[/] → {out}")

if __name__ == "__main__":
    cli()
