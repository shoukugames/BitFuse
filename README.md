# BitFuse v0.1.0

**Flick the switches. Light the fuse. Learn binary!**
Recommended ages **10+** · English and 日本語 · Windows and Linux

BitFuse teaches binary numbers with switches instead of digits. A number
appears at the top of the screen. Flick the row of switches on or off so that
together they make that number in binary, then press **IGNITE!** A spark runs
along the fuse that ties every switch together. As it passes each switch that
is ON you hear a note and see its value added up. If the total is right, the
fuse carries on to the mortars and sets off a fireworks show, with music.

## How to play

- **The number** to make is shown at the top.
- **Each switch is one bit.** From the right, the switches are worth
  1, 2, 4, 8, 16 ... Add up the switches that are ON.
- **IGNITE!** (or Enter) lights the fuse. A wrong answer fizzles out and costs
  a few seconds.
- **99-second timer** per level. Every second left when you answer correctly
  is worth **100 points**.
- **100 levels.** The numbers get larger, there are more switches, and the
  fireworks get bigger: more mortars, more shells and new kinds of burst.
  Every tenth level ends with a finale.
- The game ends when the timer reaches zero. A high score goes on the
  **Top 10** on the title screen.

Controls: click a switch to flick it, or use ← → to choose, Space to flick,
Enter to ignite and Esc to pause. F11 or Alt+Enter toggles full screen.

### Difficulty

| | Easy | Medium | Hard |
|---|---|---|---|
| Switches | 3 → 8 | 4 → 12 | 5 → 16 |
| Place values shown | always | always | levels 1–20 only |
| Running total shown | yes | no | no |
| Switches start mixed up | never | from level 41 | always |
| Wrong answer costs | 3 s | 5 s | 8 s |

## Title screen

- **Play**, **Learn Binary**, **Parents Only**, **Credits**, **Quit**
- **Difficulty**: Easy, Medium or Hard
- **Language**: English or 日本語 (switches every screen instantly)
- **Music** (BGM) on/off and **Sound FX** on/off. The background music is
  calm and ambient while you think. The fireworks fanfare follows the Music
  setting.
- **Top 10** scores

**Learn Binary** is an illustrated, animated lesson: what binary is, why
computers use it, where it is used, why it matters, how to count in binary,
place values, a step-by-step method for making any number, a page of switches
to try yourself, and how to play.

**Parents Only** opens after a simple grown-up question. It shows games
played, levels solved, the average time to solve, first-try accuracy and the
highest level reached on each difficulty, a chart of solve times, and every
attempt with its date, difficulty, level, number, result, time taken, wrong
answers and score. Records can be reset there.

## Play in the browser

BitFuse also runs in a web browser, on computers, phones and tablets, with nothing to install:
<https://shoukugames.org/play/bitfuse/> (test page). Tap the switches to flick them and tap
Ignite. Settings, scores and progress are saved in the browser.

```bash
python3 -m pip install pygame pygbag     # plus ffmpeg on PATH (or FFMPEG=/path/to/ffmpeg)
python3 tools/build_web.py               # -> build/web/: upload the folder as-is
```

The build uses [pygbag](https://pygame-web.github.io/), which also converts the sounds to OGG.
`main.py` is the web entry point; the browser-only parts switch on only in the browser.
The `.apk` file pygbag writes is its bundle of game files, not an Android app.

## Install

- **Windows:** run `BitFuse-v0.1.0.exe`. It is a single file and needs no
  installation.
- **Debian / Ubuntu:** `sudo apt install ./bitfuse_v0.1.0_amd64.deb`, then
  start **BitFuse** from the games menu or run `bitfuse`.

Settings, scores and the progress record are kept in `%APPDATA%\BitFuse`
(Windows) or `~/.local/share/bitfuse` (Linux).

## Run from source

```sh
python3 -m pip install -r requirements.txt
python3 run_game.py            # --windowed, --version, --smoke-test <file>
```

## Build

```sh
./build.sh                       # both installers into dist/
packaging/build_linux.sh         # dist/bitfuse_v0.1.0_amd64.deb
packaging/build_windows.sh       # dist/BitFuse-v0.1.0.exe (Windows Python under Wine)
```

The Linux build needs `python3-venv` and `dpkg-deb`. The Windows build needs
`wine`, `xvfb-run` and `curl`; the first run downloads Python for Windows
into `build/wine`. Each build ends by running the packaged game's built-in
self-test, which plays every screen and real levels through to the fireworks.

Developer tools (need `requirements-dev.txt`):

```sh
python3 -m pytest tests          # unit tests
python3 tools/make_audio.py      # regenerate all music and sound effects
python3 tools/make_icon.py       # regenerate the icon
BITFUSE_SHOTS=shots python3 run_game.py --smoke-test result.txt   # with screenshots
```

## Project layout

```
bitfuse/          the game (pygame)
  scenes/         title, game, intro (Learn Binary), parents, credits
  levels.py       the 100-level curve and the fireworks programme
  fireworks.py    particle fireworks
  fuse.py         the fuse and its burning spark
assets/           fonts, synthesised audio, icon
packaging/        PyInstaller spec, .desktop file, build scripts
tools/            audio and icon generators
tests/            unit tests
```

## Credits

- Created by **Shawn Rapaz**, developed with **Claude Code**
- Shouku Games: <https://shoukugames.org/> · <info@shoukugames.org>
- Fonts: M PLUS 1p and Orbitron, under the SIL Open Font License
  (`assets/fonts/OFL-*.txt`)
- Music and sound effects are original, synthesised by `tools/make_audio.py`
- Release v0.1.0, 2026-11-05

Found a bug? See [BUGREPORT.md](BUGREPORT.md).

## License

Copyright (C) 2026 Shawn Rapaz.
BitFuse is free software: you can redistribute it and/or modify it under the
terms of the **GNU General Public License v3.0** as published by the Free
Software Foundation. See [LICENSE](LICENSE).

---

## 日本語

**スイッチを切りかえて、導火線に火をつけて、2進数を学ぼう！**　対象年齢 **10才以上**

画面の上に数が表示されます。スイッチをON/OFFして、その数を2進数で作り、
**「点火！」** を押しましょう。火花がすべてのスイッチをつなぐ導火線を走り、
正解なら花火と音楽のショーが始まります。

- 持ち時間は1レベル **99秒**。正解したときの残り1秒につき **100点**。
- 全 **100レベル**。進むほど数が大きくなり、スイッチがふえ、花火も大きくなります。
- 難易度は **かんたん・ふつう・むずかしい** の3つ。
- タイトル画面で **言語（English / 日本語）**、**BGM**、**効果音** を切りかえられます。
- **2進数を学ぶ**：2進数とは何か、なぜ・どこで使われるのか、その大切さ、数え方、どんな数でも作る方法をイラストつきで説明します。
- **保護者の方へ**：プレイ回数、クリアしたレベル、平均クリア時間、一発正解率、各難易度の最高レベル、そして毎回の日時・レベル・数・結果・かかった時間・ミス・スコアを記録します。
- **トップ10** のスコアをタイトル画面に表示します。

制作：Shawn Rapaz（Claude Code で開発）・ <https://shoukugames.org/> ・ info@shoukugames.org
ライセンス：GNU GPL v3.0
