"""Music and sound effects. If there is no audio device the game stays silent."""
import os
import random

import pygame

from .paths import asset

MUSIC = {"title": "bgm_title.wav", "game": "bgm_game.wav"}
EFFECTS = {
    "click": 1, "hover": 1, "flip_on": 1, "flip_off": 1, "ignite": 1, "sizzle": 1, "launch": 3,
    "boom": 3, "boom_big": 2, "crackle": 2, "wrong": 1, "tick": 1, "time_up": 1, "new_record": 1,
    "start": 1, "mortar": 1, "fanfare": 1, "victory": 1,
}
BIT_NOTES = 16
VOLUME = {"hover": 0.2, "tick": 0.45, "click": 0.55, "sizzle": 0.5, "launch": 0.45, "crackle": 0.55,
          "boom": 0.8, "boom_big": 0.9, "mortar": 0.5, "fanfare": 0.75, "victory": 0.8}
MUSICAL = ("fanfare", "victory")  # celebration music follows the Music setting


class Audio:
    def __init__(self, settings):
        self.settings = settings
        self.ok = False
        self.sounds = {}
        self.current = None
        self.loops = {}
        self.rng = random.Random()
        self.music_channel = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 1024)
            pygame.mixer.set_num_channels(40)
            pygame.mixer.set_reserved(1)
            self.music_channel = pygame.mixer.Channel(0)
            for name, count in EFFECTS.items():
                variants = []
                for i in range(count):
                    file = f"{name}.wav" if count == 1 else f"{name}{i + 1}.wav"
                    snd = pygame.mixer.Sound(asset("audio", file))
                    snd.set_volume(VOLUME.get(name, 0.8))
                    variants.append(snd)
                self.sounds[name] = variants
            for i in range(BIT_NOTES):
                snd = pygame.mixer.Sound(asset("audio", f"bit{i:02d}.wav"))
                snd.set_volume(0.55)
                self.sounds[f"bit{i:02d}"] = [snd]
            self.ok = True
        except (pygame.error, FileNotFoundError, OSError) as error:
            print(f"Audio disabled: {error}")

    def play(self, name, pan=0.0, volume=1.0):
        if not self.ok or name not in self.sounds:
            return
        if name in MUSICAL:
            if not self.settings["bgm"]:
                return
            self.music_channel.play(self.sounds[name][0])
            return
        if not self.settings["sfx"]:
            return
        snd = self.rng.choice(self.sounds[name])
        channel = snd.play()
        if channel is not None:
            pan = max(-1.0, min(1.0, pan))
            channel.set_volume(volume * min(1.0, 1 - pan), volume * min(1.0, 1 + pan))

    def stop_music_fx(self):
        if self.ok:
            self.music_channel.fadeout(600)

    def loop(self, name, on):
        """Keep a looping effect (the burning fuse) running while 'on'."""
        if not self.ok:
            return
        playing = name in self.loops
        if on and self.settings["sfx"] and not playing:
            self.loops[name] = self.sounds[name][0].play(-1, fade_ms=80)
        elif (not on or not self.settings["sfx"]) and playing:
            channel = self.loops.pop(name)
            if channel:
                channel.fadeout(150)

    def stop_loops(self):
        for name in list(self.loops):
            self.loop(name, False)

    def duck(self, quiet):
        """Turn the background music down while the fireworks music plays."""
        if self.ok and self.current:
            pygame.mixer.music.set_volume(0.12 if quiet else 0.55)

    def music(self, which):
        if not self.ok:
            return
        if not self.settings["bgm"]:
            pygame.mixer.music.fadeout(400)
            self.music_channel.stop()
            self.current = None
            return
        if which == self.current:
            return
        self.current = which
        try:
            pygame.mixer.music.load(asset("audio", MUSIC[which]))
            pygame.mixer.music.set_volume(0.55)
            pygame.mixer.music.play(-1, fade_ms=1800)
        except pygame.error as error:
            print(f"Music unavailable: {error}")

    def refresh_music(self, which):
        self.current = None if self.settings["bgm"] else self.current
        self.music(which)


def exists():
    return os.path.exists(asset("audio", "click.wav"))
