"""Programmatic CC0 retro sound effect generator for Pushbox-Pygame.

Generates 8-bit/16-bit retro wave chimes using math and the python standard wave module.
These sounds are generated from scratch in this runtime, placing them 100% in the
Public Domain (CC0).
"""

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 22050  # 22.05 kHz is standard and lightweight


def write_wave(filename: Path, samples: list[float]) -> None:
    """Scale floating samples to 16-bit signed PCM and write standard RIFF WAVE file."""
    packed_data = b""
    for s in samples:
        # Clamp between -1.0 and 1.0 to prevent clipping
        s = max(-1.0, min(1.0, s))
        val = int(s * 32767)
        packed_data += struct.pack("<h", val)

    filename.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(filename), "wb") as w:
        w.setnchannels(1)  # Mono
        w.setsampwidth(2)  # 16-bit (2 bytes)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(packed_data)
    print(f"Generated: {filename} ({len(packed_data) // 1024} KB)")


def generate_move() -> list[float]:
    """Short, soft, high-frequency tick step sound."""
    duration = 0.04
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        envelope = 1.0 - t / duration
        # Simple sine wave with linear decay
        s = 0.12 * math.sin(2.0 * math.pi * 600.0 * t) * envelope
        samples.append(s)
    return samples


def generate_push() -> list[float]:
    """Low frequency heavier friction sweep."""
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Frequency sweep from 140 Hz down to 60 Hz
        freq = 140.0 - (140.0 - 60.0) * (t / duration)
        envelope = 1.0 - t / duration
        s = 0.28 * math.sin(2.0 * math.pi * freq * t) * envelope
        samples.append(s)
    return samples


def generate_bump() -> list[float]:
    """Muted invalid/bump impact sound."""
    duration = 0.08
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Muted rapidly descending low sweep
        freq = 90.0 - (90.0 - 40.0) * (t / duration)
        envelope = 1.0 - t / duration
        s = 0.22 * math.sin(2.0 * math.pi * freq * t) * envelope
        samples.append(s)
    return samples


def generate_target() -> list[float]:
    """Short positive chime ding (C5 and E5 harmonic arpeggio)."""
    duration = 0.25
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Dual-frequency harmony C5 (523 Hz) & E5 (659 Hz)
        note1 = math.sin(2.0 * math.pi * 523.25 * t)
        note2 = math.sin(2.0 * math.pi * 659.25 * t)
        envelope = math.exp(-7.0 * t)  # Smooth decay
        s = 0.2 * (note1 + note2) * 0.5 * envelope
        samples.append(s)
    return samples


def generate_undo() -> list[float]:
    """Short retro slide-up sweep."""
    duration = 0.14
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Up-sweep from 220 Hz to 550 Hz
        freq = 220.0 + (550.0 - 220.0) * (t / duration)
        envelope = math.sin(math.pi * t / duration)
        s = 0.22 * math.sin(2.0 * math.pi * freq * t) * envelope
        samples.append(s)
    return samples


def generate_redo() -> list[float]:
    """Short retro slide-down sweep."""
    duration = 0.14
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Down-sweep from 550 Hz to 220 Hz
        freq = 550.0 - (550.0 - 220.0) * (t / duration)
        envelope = math.sin(math.pi * t / duration)
        s = 0.22 * math.sin(2.0 * math.pi * freq * t) * envelope
        samples.append(s)
    return samples


def generate_win() -> list[float]:
    """Short, bright C-major arpeggio victory fanfare chime chord."""
    duration = 0.6
    num_samples = int(SAMPLE_RATE * duration)
    samples = [0.0] * num_samples

    # Success notes sequence with individual offsets and delays
    # C5 (523.25), E5 (659.25), G5 (783.99), C6 (1046.50)
    notes = [
        (523.25, 0.0, 0.3),
        (659.25, 0.1, 0.3),
        (783.99, 0.2, 0.3),
        (1046.50, 0.3, 0.3),
    ]

    for freq, start_delay, note_duration in notes:
        start_idx = int(SAMPLE_RATE * start_delay)
        note_samples = int(SAMPLE_RATE * note_duration)
        for i in range(note_samples):
            idx = start_idx + i
            if idx >= num_samples:
                break
            t = i / SAMPLE_RATE
            envelope = math.exp(-6.0 * t)
            # Add note frequency safely
            samples[idx] += 0.06 * math.sin(2.0 * math.pi * freq * t) * envelope

    return samples


def generate_click() -> list[float]:
    """Super clean high-frequency tick click."""
    duration = 0.02
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        envelope = 1.0 - t / duration
        s = 0.18 * math.sin(2.0 * math.pi * 1800.0 * t) * envelope
        samples.append(s)
    return samples


def main() -> None:
    """Generate all sound files and save them to src/pushbox/assets/sounds/."""
    sounds_dir = Path(__file__).parent.parent / "src" / "pushbox" / "assets" / "sounds"

    write_wave(sounds_dir / "move.wav", generate_move())
    write_wave(sounds_dir / "push.wav", generate_push())
    write_wave(sounds_dir / "bump.wav", generate_bump())
    write_wave(sounds_dir / "target.wav", generate_target())
    write_wave(sounds_dir / "undo.wav", generate_undo())
    write_wave(sounds_dir / "redo.wav", generate_redo())
    write_wave(sounds_dir / "win.wav", generate_win())
    write_wave(sounds_dir / "click.wav", generate_click())
    print(
        "\nAll 8 retro sound assets programmatically generated "
        "with 100% CC0 Public Domain compliance!"
    )


if __name__ == "__main__":
    main()
