#!/usr/bin/env python3
"""Transcribe a meeting recording locally with mlx-whisper (Apple Silicon).

Usage:
    .whisper_venv/bin/python meetings/transcribe.py <audio> [--model REPO] [--lang en]

Outputs next to the audio file:
    <name>.txt        plain transcript (paragraphs)
    <name>.timed.txt  [hh:mm:ss] timestamped segments
    <name>.srt        subtitle file
"""
import argparse
import os
import sys
import time


def fmt_ts(seconds: float, srt: bool = False) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    if srt:
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--model", default="mlx-community/whisper-large-v3-turbo")
    ap.add_argument("--lang", default="en")
    args = ap.parse_args()

    import mlx_whisper

    audio = os.path.abspath(args.audio)
    if not os.path.exists(audio):
        print(f"[err] file not found: {audio}", file=sys.stderr)
        return 1

    base = os.path.splitext(audio)[0]
    print(f"[info] model = {args.model}")
    print(f"[info] audio = {audio}")
    print("[info] transcribing... (model downloads on first run)")
    t0 = time.time()

    result = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo=args.model,
        language=args.lang,
        verbose=False,
        word_timestamps=False,
    )
    dt = time.time() - t0
    segments = result.get("segments", [])
    print(f"[info] done in {dt:.0f}s, {len(segments)} segments")

    # 1) plain transcript
    full = (result.get("text") or "").strip()
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(full + "\n")

    # 2) timestamped transcript
    with open(base + ".timed.txt", "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"[{fmt_ts(seg['start'])}] {seg['text'].strip()}\n")

    # 3) srt
    with open(base + ".srt", "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{fmt_ts(seg['start'], srt=True)} --> {fmt_ts(seg['end'], srt=True)}\n")
            f.write(seg["text"].strip() + "\n\n")

    print(f"[ok] {base}.txt")
    print(f"[ok] {base}.timed.txt")
    print(f"[ok] {base}.srt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
