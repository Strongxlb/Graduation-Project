#!/usr/bin/env python3
"""Transcribe an audio file with faster-whisper.

Produces three outputs next to the input file (matching the 6.18 meeting):
  - <name>.srt        standard subtitle file with timestamps
  - <name>.timed.txt  [HH:MM:SS] text, one line per segment
  - <name>.txt        plain running transcript
"""
import sys
import os
from faster_whisper import WhisperModel


def fmt_ts(seconds: float, sep: str = ",") -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600 * 1000)
    m, ms = divmod(ms, 60 * 1000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def fmt_hms(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main():
    audio = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "small.en"
    base = os.path.splitext(audio)[0]

    print(f"Loading model: {model_size}", flush=True)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("Transcribing...", flush=True)
    segments, info = model.transcribe(
        audio,
        language="en",
        vad_filter=True,
        beam_size=5,
    )
    print(f"Detected language: {info.language} (p={info.language_probability:.2f}), "
          f"duration={info.duration:.1f}s", flush=True)

    # Write incrementally so partial progress survives interruptions.
    srt_f = open(base + ".srt", "w", encoding="utf-8")
    timed_f = open(base + ".timed.txt", "w", encoding="utf-8")
    txt_f = open(base + ".txt", "w", encoding="utf-8")

    first = True
    for i, seg in enumerate(segments, start=1):
        text = seg.text.strip()
        srt_f.write(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{text}\n\n")
        srt_f.flush()
        timed_f.write(f"[{fmt_hms(seg.start)}] {text}\n")
        timed_f.flush()
        txt_f.write(("" if first else " ") + text)
        txt_f.flush()
        first = False
        # progress heartbeat
        print(f"[{fmt_hms(seg.start)}] {text}", flush=True)

    txt_f.write("\n")
    srt_f.close()
    timed_f.close()
    txt_f.close()

    print("\nDONE. Wrote:", flush=True)
    print(f"  {base}.srt", flush=True)
    print(f"  {base}.timed.txt", flush=True)
    print(f"  {base}.txt", flush=True)


if __name__ == "__main__":
    main()
