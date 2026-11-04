#!/usr/bin/env python3
"""Synthesise every sound in BitFuse into assets/audio/*.wav.

Run this only when the sound design changes (needs numpy; the game itself does not).
All music is original and generated here: slow ambient pads and soft bells for
puzzling, and a bright fanfare for the fireworks.
"""
import os
import wave

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "audio")
RNG = np.random.default_rng(20261105)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def save(name, data, rate):
    """data: float array, mono (n,) or stereo (n, 2), range about -1..1"""
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        data = data[:, None]
    peak = np.max(np.abs(data)) or 1.0
    data = data / peak * 0.89
    pcm = (data * 32767).astype("<i2")
    with wave.open(os.path.join(OUT, name), "wb") as handle:
        handle.setnchannels(pcm.shape[1])
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm.tobytes())
    print(f"{name}: {len(pcm) / rate:.1f}s")


def lowpass(signal, rate, cutoff):
    spec = np.fft.rfft(signal, axis=0)
    freqs = np.fft.rfftfreq(signal.shape[0], 1 / rate)
    curve = 1 / (1 + (freqs / cutoff) ** 4)
    if signal.ndim == 2:
        curve = curve[:, None]
    return np.fft.irfft(spec * curve, n=signal.shape[0], axis=0)


def circular_reverb(signal, rate, seconds=4.0, mix=0.55, seed=1):
    """Convolve with decaying noise, wrapping the tail so the loop stays seamless."""
    rng = np.random.default_rng(seed)
    n = signal.shape[0]
    out = np.zeros((n, 2))
    length = int(seconds * rate)
    t = np.arange(length) / rate
    for ch in range(2):
        ir = rng.standard_normal(length) * np.exp(-t * 6.9 / seconds)
        ir = lowpass(ir, rate, 3500)
        ir[: int(0.012 * rate)] *= np.linspace(0, 1, int(0.012 * rate))
        ir /= np.sqrt(np.sum(ir ** 2))
        size = n  # circular convolution over exactly one loop length
        wet = np.fft.irfft(np.fft.rfft(signal[:, ch], size) * np.fft.rfft(ir, size), size)
        out[:, ch] = signal[:, ch] * (1 - mix) + wet * mix * 1.6
    return out


def envelope(n, rate, attack, release):
    env = np.ones(n)
    a = min(n, max(1, int(attack * rate)))
    r = min(n - a, max(1, int(release * rate)))
    env[:a] = np.linspace(0, 1, a) ** 2
    env[n - r:] *= np.linspace(1, 0, r) ** 2
    return env


def pad_voice(m, seconds, rate, bright=1.0):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    out = np.zeros(n)
    for detune in (-0.07, 0.0, 0.08):
        f = midi_hz(m + detune)
        phase = RNG.uniform(0, 2 * np.pi)
        # soft saw from a few harmonics
        for h, amp in ((1, 1.0), (2, 0.42 * bright), (3, 0.2 * bright), (4, 0.09 * bright), (5, 0.05 * bright)):
            out += amp * np.sin(2 * np.pi * f * h * t + phase * h)
    lfo = 1 + 0.18 * np.sin(2 * np.pi * RNG.uniform(0.07, 0.15) * t + RNG.uniform(0, 6))
    return out * lfo * envelope(n, rate, seconds * 0.35, seconds * 0.45) / 3


def bell(m, seconds, rate, decay=2.2):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m)
    out = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
           + 0.18 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6))
    env = np.exp(-t * decay)
    env[: int(0.004 * rate)] *= np.linspace(0, 1, int(0.004 * rate))
    return out * env


def place(buffer, sound, start, gain=1.0, pan=0.0):
    """Add a mono sound into a stereo loop buffer, wrapping around the end."""
    n = buffer.shape[0]
    left = gain * np.sqrt((1 - pan) / 2)
    right = gain * np.sqrt((1 + pan) / 2)
    idx = (np.arange(len(sound)) + start) % n
    np.add.at(buffer[:, 0], idx, sound * left)
    np.add.at(buffer[:, 1], idx, sound * right)


def ambient_track(rate, chords, chord_seconds, scale, bells_per_chord, root_bass, seed, bright):
    global RNG
    RNG = np.random.default_rng(seed)
    total = len(chords) * chord_seconds
    n = int(total * rate)
    buf = np.zeros((n, 2))
    overlap = 2.5
    for i, chord in enumerate(chords):
        start = int((i * chord_seconds - overlap / 2) * rate)
        for j, m in enumerate(chord):
            voice = pad_voice(m, chord_seconds + overlap, rate, bright)
            place(buf, voice, start, 0.16, pan=(j / max(1, len(chord) - 1)) * 1.2 - 0.6)
        bass = pad_voice(root_bass[i], chord_seconds + overlap, rate, 0.3)
        place(buf, bass, start, 0.22, 0.0)
        # gentle bells drawn from the scale, never crowded
        times = np.sort(RNG.uniform(0.3, chord_seconds - 0.5, bells_per_chord))
        for k, tm in enumerate(times):
            note = int(RNG.choice(scale))
            place(buf, bell(note, 4.5, rate, decay=RNG.uniform(1.2, 2.0)),
                  int((i * chord_seconds + tm) * rate), RNG.uniform(0.05, 0.09), RNG.uniform(-0.7, 0.7))
    # a soft wind-like noise bed
    noise = lowpass(RNG.standard_normal((n, 2)), rate, 500)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / n * 3)[:, None]
    buf += noise * 0.012 * swell
    buf = lowpass(buf, rate, 5200)
    return circular_reverb(buf, rate, seconds=5.0, mix=0.5, seed=seed)


def tone(freq, seconds, rate, wave_kind="sine", decay=8.0, attack=0.003):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = np.asarray(freq) if np.ndim(freq) else np.full(n, freq)
    phase = 2 * np.pi * np.cumsum(f) / rate
    if wave_kind == "sine":
        s = np.sin(phase)
    elif wave_kind == "tri":
        s = 2 / np.pi * np.arcsin(np.sin(phase))
    elif wave_kind == "square":
        s = np.tanh(np.sin(phase) * 4)
    else:
        s = np.sin(phase) + 0.3 * np.sin(2 * phase)
    env = np.exp(-t * decay)
    a = max(1, int(attack * rate))
    env[:a] *= np.linspace(0, 1, a)
    return s * env


def noise(seconds, rate, seed=0):
    return np.random.default_rng(seed).standard_normal(int(seconds * rate))


def highpass(signal, rate, cutoff):
    return signal - lowpass(signal, rate, cutoff)


def brass(m, seconds, rate, bright=1.0):
    """A warm synth-brass note with a soft attack and a little vibrato."""
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1))
    phase = 2 * np.pi * np.cumsum(f) / rate
    out = np.zeros(n)
    for h in range(1, 9):
        out += np.sin(phase * h) / h ** (1.6 - 0.4 * bright)
    env = envelope(n, rate, 0.03, min(seconds * 0.5, 0.25)) * (0.75 + 0.25 * np.exp(-t * 4))
    return out * env


def fanfare_track(rate, melody, chords, beat, tail=3.0, seed=4, grand=False):
    """melody: (beat, length_beats, midi); chords: (beat, length_beats, [midi..])"""
    end = max(b + l for b, l, _ in melody + chords) * beat
    n = int((end + tail) * rate)
    buf = np.zeros((n, 2))
    for b, length, m in melody:
        place(buf, brass(m, length * beat + 0.15, rate), int(b * beat * rate), 0.34, -0.15)
        place(buf, bell(m + 12, 2.5, rate, decay=2.5), int(b * beat * rate), 0.1, 0.4)
    for b, length, notes in chords:
        for j, m in enumerate(notes):
            place(buf, pad_voice(m, length * beat + 1.2, rate, 0.8), int(b * beat * rate), 0.13,
                  j / max(1, len(notes) - 1) - 0.5)
        place(buf, brass(notes[0] - 12, length * beat * 0.9, rate, 0.4), int(b * beat * rate), 0.25, 0.0)
        # timpani-like hit on each chord
        hit = tone(midi_hz(notes[0] - 24), 1.2, rate, "sine", decay=3.5)
        hit += lowpass(noise(1.2, rate, int(b)) * np.exp(-np.arange(len(hit)) / rate * 18), rate, 600) * 0.6
        place(buf, hit, int(b * beat * rate), 0.45, 0.0)
    # sparkling chimes on top
    rng = np.random.default_rng(seed)
    for k in range(int(end / beat * (3 if grand else 2))):
        m = int(rng.choice([84, 86, 88, 91, 93, 96]))
        place(buf, bell(m, 2.0, rate, decay=3.0), int(rng.uniform(0, end) * rate), 0.04, rng.uniform(-0.8, 0.8))
    buf = lowpass(buf, rate, 7000)
    out = np.zeros_like(buf)
    # simple non-circular reverb so the ending rings out naturally
    for ch in range(2):
        length = int(2.5 * rate)
        tt = np.arange(length) / rate
        ir = np.random.default_rng(seed + ch).standard_normal(length) * np.exp(-tt * 2.6)
        ir = lowpass(ir, rate, 4000)
        ir /= np.sqrt(np.sum(ir ** 2))
        wet = np.fft.irfft(np.fft.rfft(buf[:, ch], n + length) * np.fft.rfft(ir, n + length), n + length)[:n]
        out[:, ch] = buf[:, ch] * 0.7 + wet * 0.55
    fade = int(0.8 * rate)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out


def music():
    rate = 22050
    # Title: warm F major colours, airy and welcoming
    chords = [[65, 69, 72, 76], [62, 65, 69, 72], [58, 62, 65, 69, 72], [60, 64, 67, 70],
              [57, 60, 64, 69], [58, 62, 65, 70], [55, 58, 62, 65, 69], [60, 65, 67, 72]]
    bass = [41, 38, 34, 36, 33, 34, 31, 36]
    scale = [77, 79, 81, 84, 86, 89, 91, 93]
    save("bgm_title.wav", ambient_track(rate, chords, 7, scale, 3, bass, 31, 0.85), rate)
    # Puzzle: very calm E-flat major pads, slow, sparse bells so it never distracts
    chords = [[63, 67, 70, 74], [60, 63, 67, 70], [56, 60, 63, 67, 70], [58, 62, 65, 70],
              [63, 67, 70, 77], [55, 58, 62, 67], [56, 60, 65, 68], [58, 63, 65, 70]]
    bass = [39, 36, 32, 34, 39, 31, 32, 34]
    scale = [75, 77, 79, 82, 84, 87, 89]
    save("bgm_game.wav", ambient_track(rate, chords, 9, scale, 2, bass, 47, 0.6), rate)

    rate = 32000
    beat = 0.36
    melody = [(0, 0.5, 67), (0.5, 0.5, 72), (1, 0.5, 76), (1.5, 1.5, 79), (3, 0.5, 76), (3.5, 0.5, 79),
              (4, 0.5, 81), (4.5, 0.5, 84), (5, 1.0, 81), (6, 1.0, 79), (7, 0.5, 77), (7.5, 0.5, 76),
              (8, 0.5, 74), (8.5, 0.5, 76), (9, 0.5, 77), (9.5, 0.5, 79), (10, 0.5, 76), (10.5, 0.5, 74),
              (11, 0.5, 72), (11.5, 0.5, 74), (12, 4.0, 72)]
    chords = [(0, 3, [48, 60, 64, 67]), (3, 3, [53, 60, 65, 69]), (6, 2, [55, 59, 62, 67]),
              (8, 2, [53, 57, 60, 65]), (10, 2, [55, 59, 62, 65]), (12, 4, [48, 60, 64, 67, 72])]
    save("fanfare.wav", fanfare_track(rate, melody, chords, beat, seed=9), rate)
    # Victory after level 100: longer and grander
    melody2 = melody[:12] + [(n + 8, l, m) for n, l, m in melody[:12]] + [
        (16, 0.5, 79), (16.5, 0.5, 81), (17, 0.5, 83), (17.5, 0.5, 84), (18, 0.5, 86), (18.5, 0.5, 88),
        (19, 1, 86), (20, 5, 84)]
    chords2 = [(0, 3, [48, 60, 64, 67]), (3, 3, [53, 60, 65, 69]), (6, 2, [55, 59, 62, 67]),
               (8, 3, [57, 60, 64, 69]), (11, 3, [53, 57, 60, 65]), (14, 2, [55, 59, 62, 67]),
               (16, 2, [53, 57, 60, 65, 69]), (18, 2, [55, 59, 62, 67, 71]), (20, 5, [48, 60, 64, 67, 72, 76])]
    save("victory.wav", fanfare_track(rate, melody2, chords2, 0.38, tail=3.5, seed=13, grand=True), rate)


def effects():
    rate = 44100

    def cat(*parts):
        return np.concatenate(parts)

    def silence(s):
        return np.zeros(int(s * rate))

    def mix(*sounds):
        n = max(len(s) for s in sounds)
        out = np.zeros(n)
        for s in sounds:
            out[: len(s)] += s
        return out

    def stereo(mono, verb=0.25, tail=0.6, decay=12, seed=5):
        pad = np.concatenate([mono, np.zeros(int(tail * rate))])
        rng = np.random.default_rng(seed)
        length = int(tail * 0.9 * rate)
        t = np.arange(length) / rate
        out = np.zeros((len(pad), 2))
        for ch in range(2):
            ir = rng.standard_normal(length) * np.exp(-t * decay)
            ir /= np.sqrt(np.sum(ir ** 2))
            wet = np.fft.irfft(np.fft.rfft(pad, len(pad) + length) * np.fft.rfft(ir, len(pad) + length),
                               len(pad) + length)[: len(pad)]
            out[:, ch] = pad * (1 - verb) + wet * verb
        return out

    def env_exp(seconds, decay, attack=0.002):
        n = int(seconds * rate)
        t = np.arange(n) / rate
        e = np.exp(-t * decay)
        a = max(1, int(attack * rate))
        e[:a] *= np.linspace(0, 1, a)
        return e

    save("click.wav", stereo(tone(1250, 0.06, rate, decay=60) * 0.6, 0.1), rate)
    save("hover.wav", tone(2300, 0.03, rate, decay=120) * 0.3, rate)
    # Toggle switch: a crisp metal clack with a small thump
    for name, pitch in (("flip_on", 1.0), ("flip_off", 0.82)):
        snap = highpass(noise(0.05, rate, 3), rate, 2500) * env_exp(0.05, 120)
        ping = mix(tone(3100 * pitch, 0.06, rate, decay=90) * 0.5, tone(5200 * pitch, 0.04, rate, decay=140) * 0.25)
        thump = tone(np.linspace(240 * pitch, 120, int(0.08 * rate)), 0.08, rate, decay=45) * 0.8
        save(f"{name}.wav", stereo(mix(snap * 0.7, ping, thump), 0.12, 0.3), rate)
    # Match strike, then a soft "whoomph" as the fuse catches
    scratch = highpass(noise(0.35, rate, 11), rate, 1800) * (env_exp(0.35, 7) * (0.6 + 0.4 * np.sin(np.linspace(0, 40, int(0.35 * rate)))))
    whoomph = lowpass(noise(0.6, rate, 12), rate, 900) * env_exp(0.6, 6, 0.08)
    save("ignite.wav", stereo(mix(scratch * 0.7, cat(silence(0.25), whoomph)), 0.2), rate)
    # Burning fuse: a seamless 2 second hiss with little pops
    n = 2 * rate
    hiss = highpass(lowpass(noise(2, rate, 21), rate, 7000), rate, 2200) * 0.35
    hiss *= 0.75 + 0.25 * np.sin(2 * np.pi * np.arange(n) / n * 6)
    rng = np.random.default_rng(22)
    for _ in range(60):
        at = rng.integers(0, n - 800)
        pop = highpass(noise(0.015, rate, int(at)), rate, 3000) * env_exp(0.015, 300) * rng.uniform(0.4, 1.2)
        hiss[at:at + len(pop)] += pop
    save("sizzle.wav", hiss, rate)
    # Mortar launches: a thump, a rush of air and sometimes a whistle
    for i in range(3):
        thump = tone(np.linspace(110, 45, int(0.35 * rate)), 0.35, rate, decay=10) * 1.2
        rush = highpass(noise(1.1, rate, 30 + i), rate, 900) * env_exp(1.1, 3.5, 0.05) * 0.4
        parts = [thump, rush]
        if i != 1:
            f = np.linspace(1800 + 300 * i, 2600 + 300 * i, int(1.0 * rate)) + 40 * np.sin(np.arange(int(rate)) / rate * 60)
            whistle = tone(f, 1.0, rate, "sine", decay=1.5, attack=0.15) * 0.22
            parts.append(cat(silence(0.05), whistle))
        save(f"launch{i + 1}.wav", stereo(mix(*parts), 0.25, 0.8), rate)
    # Bursts: deep booms with a long echo off the city
    for i in range(3):
        length = 2.2
        body = lowpass(noise(length, rate, 40 + i), rate, 420 + 120 * i) * env_exp(length, 3.2, 0.004) * 1.6
        crack = highpass(noise(0.08, rate, 50 + i), rate, 1500) * env_exp(0.08, 40) * 0.8
        sub = tone(np.linspace(70, 38, int(0.9 * rate)), 0.9, rate, decay=4.5) * 1.1
        save(f"boom{i + 1}.wav", stereo(mix(body, crack, sub), 0.45, 1.6, 3.0, 60 + i), rate)
    for i in range(2):
        length = 3.0
        body = lowpass(noise(length, rate, 70 + i), rate, 330) * env_exp(length, 2.2, 0.004) * 1.8
        crack = highpass(noise(0.12, rate, 80 + i), rate, 1200) * env_exp(0.12, 30)
        sub = tone(np.linspace(60, 30, int(1.4 * rate)), 1.4, rate, decay=3) * 1.3
        save(f"boom_big{i + 1}.wav", stereo(mix(body, crack, sub), 0.5, 2.2, 2.2, 90 + i), rate)
    # Crackle: hundreds of tiny pops spreading out
    for i in range(2):
        n = int(2.2 * rate)
        out = np.zeros(n)
        rng = np.random.default_rng(100 + i)
        for _ in range(240):
            at = int(rng.beta(1.6, 3.0) * (n - 1000))
            pop = highpass(noise(0.01, rate, int(at) + i), rate, 2500) * env_exp(0.01, 400) * rng.uniform(0.3, 1.0)
            out[at:at + len(pop)] += pop
        save(f"crackle{i + 1}.wav", stereo(out, 0.35, 0.8), rate)
    # Wrong answer: the spark fizzles out
    fizz = highpass(noise(0.7, rate, 120), rate, 1500) * env_exp(0.7, 5) * 0.5
    bwomp = cat(tone(311, 0.18, rate, "tri", decay=6), tone(233, 0.35, rate, "tri", decay=5)) * 0.8
    save("wrong.wav", stereo(mix(fizz, bwomp), 0.3), rate)
    save("tick.wav", tone(1600, 0.05, rate, "sine", decay=70) * 0.7, rate)
    notes = [67, 63, 60, 55]
    seq = mix(*[cat(silence(i * 0.22), tone(midi_hz(m), 0.6, rate, "tri", decay=4)) for i, m in enumerate(notes)])
    save("time_up.wav", stereo(seq, 0.4), rate)
    save("start.wav", stereo(mix(tone(midi_hz(67), 0.5, rate, "bell", decay=5),
                                 cat(silence(0.1), tone(midi_hz(74), 0.7, rate, "bell", decay=4))), 0.35), rate)
    save("new_record.wav", stereo(mix(*[cat(silence(i * 0.08), tone(midi_hz(m), 0.8, rate, "bell", decay=4))
                                        for i, m in enumerate([72, 79, 84, 88, 91])]), 0.4), rate)
    mortar = highpass(noise(0.3, rate, 140), rate, 2500) * env_exp(0.3, 10) * 0.4
    save("mortar.wav", stereo(mix(mortar, tone(900, 0.05, rate, decay=60) * 0.2), 0.2), rate)
    # One soft bell per switch the spark passes: a rising pentatonic tune
    scale = [67, 69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96, 98, 100, 103]
    for i, m in enumerate(scale):
        b = mix(bell(m, 1.4, rate, decay=3.0) * 0.6, tone(midi_hz(m), 0.5, rate, "tri", decay=9) * 0.2)
        save(f"bit{i:02d}.wav", stereo(b, 0.3, 0.6), rate)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    effects()
    music()
