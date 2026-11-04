# Reporting a bug in BitFuse

Thank you for helping make BitFuse better! A good bug report lets us find and
fix the problem quickly.

**Where to send it:** email **info@shoukugames.org** with the subject
`BitFuse bug: <short summary>`, or open an issue on the project's repository.

## Before you report

1. Check you have the latest version (shown at the bottom of the title screen
   and in **Credits**).
2. Try to make the problem happen a second time and note the exact steps.

## Copy this template

```
BitFuse version:       (e.g. v0.1.0, from the Credits screen)
Operating system:      (e.g. Windows 11, Ubuntu 24.04, Debian 12)
How installed:         (.exe / .deb / from source)
Language setting:      (English / 日本語)
Difficulty and level:  (e.g. Medium, level 41)
Number on screen:      (the number you had to make, e.g. 202)
Switches you set:      (e.g. 11001010, left to right)

What happened:

What I expected to happen:

Steps to make it happen again:
1.
2.
3.

How often:             (every time / sometimes / once)
```

## Helpful extras

- **Screenshot or video** of the problem. For "my answer was right but it
  fizzled", a screenshot of the switches is the most useful thing you can send.
- **Crash log:** if the game closes unexpectedly it writes `crash.log` to its
  data folder. Please attach it.
  - Windows: `%APPDATA%\BitFuse\crash.log`
  - Linux: `~/.local/share/bitfuse/crash.log`
- **Progress file**, if the bug is about the Parents Only screen:
  `progress.json` in the same folder. It contains only dates, levels, numbers,
  times and scores, no personal information.
- **From source:** run `python3 run_game.py --windowed` in a terminal and copy
  any error text it prints.
- **Self-test:** `bitfuse --smoke-test result.txt` (or the .exe with the same
  option) runs the built-in check and writes the result to `result.txt`.

## Known limitations

- No sound on a computer without a working audio device; the game still runs.
- Typing Japanese names on the Top 10 needs your system's input method (IME)
  to work with the game window.
- Very old graphics hardware may run the biggest fireworks shows (levels 90+)
  below 60 frames per second.

---

# バグの報告（日本語）

BitFuse の改善にご協力いただきありがとうございます。

**送り先：** **info@shoukugames.org** へ、件名 `BitFuse bug: <かんたんな内容>` でメールしてください。

## 報告の前に

1. 最新版か確認してください（タイトル画面の下と「クレジット」に表示されています）。
2. もう一度同じことが起きるか試して、手順をメモしてください。

## テンプレート

```
BitFuseのバージョン：（例：v0.1.0）
OS：                  （例：Windows 11、Ubuntu 24.04）
インストール方法：      （.exe / .deb / ソースから）
言語設定：             （English / 日本語）
難易度とレベル：        （例：ふつう、レベル41）
画面の数：             （作る数。例：202）
スイッチの状態：        （左から。例：11001010）

起きたこと：

期待していたこと：

再現手順：
1.
2.
3.

頻度：                 （毎回 / ときどき / 一度だけ）
```

## あると助かるもの

- 問題のスクリーンショットや動画
- ゲームが突然終了した場合は `crash.log`
  - Windows：`%APPDATA%\BitFuse\crash.log`
  - Linux：`~/.local/share/bitfuse/crash.log`
- 「保護者の方へ」画面の問題なら `progress.json`（個人情報は含まれません）
