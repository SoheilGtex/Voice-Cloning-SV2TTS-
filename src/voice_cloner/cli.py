from __future__ import annotations

import os
from pathlib import Path

import click
from rich.console import Console

from .utils.audio import load_wav_mono, save_wav_16k_mono, ensure_16k_mono
from .backends.rtvc_wrapper import SV2TTSBackend

console = Console()

@click.group()
def cli():
    """Voice Cloner CLI (SV2TTS Wrapper)"""
    pass

@cli.command(help="Clone a voice from a speaker reference and synthesize target text.")
@click.option("--speaker", type=click.Path(exists=True, dir_okay=False), required=True, help="Path to speaker WAV (mono, 16kHz recommended).")
@click.option("--text", type=str, required=True, help="Text to synthesize.")
@click.option("--out", type=click.Path(dir_okay=False), default="out.wav", help="Output WAV path.")
@click.option("--rtvc", type=click.Path(exists=True, file_okay=False), default=None, help="Path to RTVC repo (fallback to VOICE_CLONER_RTVC_PATH).")
def clone(speaker: str, text: str, out: str, rtvc: str | None):
    # Ethics banner
    console.print("[bold yellow]Use with consent only. Label synthetic audio. Follow local laws.[/]")

    # Resolve backend path
    rtvc_path = Path(rtvc) if rtvc else Path(os.environ.get("VOICE_CLONER_RTVC_PATH", ""))
    if not rtvc_path.exists():
        console.print("[red]RTVC path not found. Set --rtvc or VOICE_CLONER_RTVC_PATH.[/]")
        raise SystemExit(2)

    # Ensure audio format
    wav, sr = load_wav_mono(Path(speaker))
    wav16 = ensure_16k_mono(wav, sr)

    # Run backend
    backend = SV2TTSBackend(rtvc_path)
    y = backend.clone_to_waveform(wav16, text)

    save_wav_16k_mono(Path(out), y)
    console.print(f"[bold green]Done[/] → {out}")

if __name__ == "__main__":
    cli()
