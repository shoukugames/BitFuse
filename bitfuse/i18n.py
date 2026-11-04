"""Every piece of on-screen text, in English and Japanese."""

LANG = {"current": "en"}

STRINGS = {
    "title_sub": ("Flick the switches. Light the fuse. Learn binary!",
                  "スイッチを切りかえて、導火線に火をつけて、2進数を学ぼう！"),
    "play": ("Play", "プレイ"),
    "intro": ("Learn Binary", "2進数を学ぶ"),
    "parents": ("Parents Only", "保護者の方へ"),
    "credits": ("Credits", "クレジット"),
    "quit": ("Quit", "終了"),
    "settings": ("Settings", "設定"),
    "difficulty": ("Difficulty", "難易度"),
    "easy": ("Easy", "かんたん"),
    "medium": ("Medium", "ふつう"),
    "hard": ("Hard", "むずかしい"),
    "easy_info": ("3 to 8 switches. Place values and a running total are shown. Wrong answer: -3 s.",
                  "スイッチ3〜8個。位の数と合計が表示されます。まちがい：−3秒。"),
    "medium_info": ("4 to 12 switches. No running total. From level 41 switches start mixed up. Wrong: -5 s.",
                    "スイッチ4〜12個。合計は表示されません。レベル41からスイッチがバラバラに。まちがい：−5秒。"),
    "hard_info": ("5 to 16 switches, mixed up from the start. Place values vanish after level 20. Wrong: -8 s.",
                  "スイッチ5〜16個、最初からバラバラ。レベル21から位の数が消えます。まちがい：−8秒。"),
    "bgm": ("Music", "BGM"),
    "sfx": ("Sound FX", "効果音"),
    "on": ("ON", "ON"),
    "off": ("OFF", "OFF"),
    "language": ("Language", "言語"),
    "ages": ("Recommended ages 10+", "対象年齢 10才以上"),
    "top10": ("Top 10", "トップ10"),
    "no_scores": ("No scores yet.\nBe the first!", "まだ記録がありません。\n一番乗りしよう！"),
    "back": ("Back", "もどる"),
    "level": ("Level", "レベル"),
    "score": ("Score", "スコア"),
    "time": ("Time", "時間"),
    "make": ("Make this number with the switches", "スイッチでこの数を作ろう"),
    "ignite": ("IGNITE!", "点火！"),
    "menu": ("Menu", "メニュー"),
    "total": ("Your switches make", "スイッチの合計"),
    "start": ("Start!", "スタート！"),
    "next": ("Next Level", "次のレベル"),
    "skip": ("Click to continue", "クリックで次へ"),
    "paused": ("Paused", "一時停止"),
    "resume": ("Resume", "つづける"),
    "to_title": ("Quit to Title", "タイトルへ"),
    "correct": ("Correct!", "正解！"),
    "bonus": ("{s} seconds left × 100 = {p} points", "残り{s}秒 × 100 = {p}点"),
    "wrong_total": ("Not quite! Your switches make {v}, but the number is {t}.",
                    "おしい！スイッチの合計は{v}、目標は{t}です。"),
    "wrong_high": ("Not quite! That is too high.", "おしい！大きすぎます。"),
    "wrong_low": ("Not quite! That is too low.", "おしい！小さすぎます。"),
    "penalty": ("-{s} s", "−{s}秒"),
    "time_up": ("Time's up!", "時間切れ！"),
    "game_over": ("Game Over", "ゲームオーバー"),
    "victory": ("You mastered all 100 levels!", "全100レベル クリア！"),
    "final_score": ("Final score", "最終スコア"),
    "reached": ("Reached level {n} on {d}", "{d}でレベル{n}まで到達"),
    "new_high": ("New Top 10 score! Type your name:", "トップ10入り！名前を入力してね："),
    "save": ("Save", "保存"),
    "retry": ("Play Again", "もう一度"),
    "level_intro": ("Level {n}", "レベル {n}"),
    "level_bits": ("{b} switches", "スイッチ {b}個"),
    "level_hint_values": ("The numbers above the switches are their place values.",
                          "スイッチの上の数字は、そのスイッチの「位の数」です。"),
    "level_hint_hidden": ("No place values from now on. Remember: 1, 2, 4, 8, 16 ... from the right!",
                          "ここから位の数は表示されません。右から 1, 2, 4, 8, 16 … だよ！"),
    "level_hint_scramble": ("Some switches start ON. Flick them on or off!",
                            "いくつかのスイッチは最初からONです。ON/OFFを切りかえよう！"),
    "controls": ("Click a switch to flick it.  Keys: ← → choose, Space flick, Enter ignite, Esc pause",
                 "スイッチをクリックで切りかえ。キー：←→選択、スペース切りかえ、Enter点火、Esc一時停止"),
    # Parents
    "parent_gate": ("Grown-ups: answer this to continue.", "保護者の方：答えを入力してください。"),
    "parent_wrong": ("That's not right. Try this one.", "ちがいます。こちらを解いてください。"),
    "progress": ("Progress Record", "進み具合の記録"),
    "games_played": ("Games played", "プレイ回数"),
    "levels_solved": ("Levels solved", "クリアしたレベル"),
    "avg_time": ("Average time to solve", "平均クリア時間"),
    "accuracy": ("First-try accuracy", "一発正解率"),
    "best_level": ("Highest level solved", "最高クリアレベル"),
    "chart_title": ("Seconds to solve, last 40 levels solved", "クリアまでの秒数（最近の40レベル）"),
    "recent": ("Recent attempts", "最近の記録"),
    "col_when": ("Date", "日時"),
    "col_diff": ("Difficulty", "難易度"),
    "col_level": ("Level", "レベル"),
    "col_number": ("Number", "数"),
    "col_result": ("Result", "結果"),
    "col_time": ("Time", "時間"),
    "col_wrong": ("Wrong", "ミス"),
    "col_score": ("Score", "スコア"),
    "solved": ("Solved", "クリア"),
    "timeout": ("Time up", "時間切れ"),
    "quit_r": ("Quit", "中断"),
    "no_attempts": ("Nothing recorded yet. Records appear after the first game.",
                    "まだ記録はありません。最初のゲームの後に表示されます。"),
    "reset": ("Reset records", "記録をリセット"),
    "reset_confirm": ("Click again to erase", "もう一度押すと消去"),
    "page": ("Page {a} / {b}", "{a} / {b} ページ"),
    # Credits
    "credits_title": ("Credits", "クレジット"),
    "version": ("Version", "バージョン"),
    "date": ("Release date", "リリース日"),
    "creator": ("Created by", "制作"),
    "built_with": ("Developed with", "開発協力"),
    "website": ("Website", "ウェブサイト"),
    "email": ("Email", "メール"),
    "license": ("License", "ライセンス"),
    "license_text": ("BitFuse is free software under the GNU General Public License v3.0. You may share and change it under the same terms.",
                     "BitFuseはGNU一般公衆利用許諾書 v3.0のフリーソフトウェアです。同じ条件で共有・改変できます。"),
    "view_license": ("View License", "ライセンスを見る"),
    "fonts_credit": ("Fonts: M PLUS 1p and Orbitron (SIL Open Font License)",
                     "フォント：M PLUS 1p、Orbitron（SIL Open Font License）"),
    "audio_credit": ("Music and sound: original, synthesised for BitFuse", "音楽・効果音：BitFuseのためのオリジナル"),
    "intro_title": ("Learn Binary", "2進数を学ぼう"),
    "prev": ("◀ Prev", "◀ 前へ"),
    "next_page": ("Next ▶", "次へ ▶"),
    "try_total": ("These switches make", "このスイッチの合計"),
    "try_clear": ("All off", "全部OFF"),
}

# Introduction: (key, title, body). Illustrations are drawn by the intro scene.
LESSONS = [
    ("what",
     ("What is binary?", "2進数ってなに？"),
     ("Binary is a way of writing numbers using only two digits: 0 and 1.\n\n"
      "We usually count with ten digits (0 to 9). That is called decimal. Binary is called "
      "\"base 2\" because it has just two.\n\n"
      "Think of a light switch. It can only be OFF or ON. OFF means 0 and ON means 1. "
      "One switch, one 0 or 1, is called a bit (short for \"binary digit\").\n\n"
      "In BitFuse every switch is one bit!",
      "2進数は、0と1の2つの数字だけを使って数を書く方法です。\n\n"
      "ふだん私たちは0〜9の10個の数字で数えます。これを10進数といいます。2進数は数字が2つだけなので"
      "「2を底（てい）とする数」ともよばれます。\n\n"
      "電気のスイッチを思いうかべてください。OFFかONのどちらかしかありません。OFFが0、ONが1です。"
      "この0か1を1つ表すものを「ビット」といいます（binary digit＝2進数の数字の略）。\n\n"
      "BitFuseでは、スイッチ1個が1ビットです！")),
    ("why",
     ("Why do computers use binary?", "なぜ2進数を使うの？"),
     ("A computer chip is packed with billions of tiny switches called transistors. "
      "Each one is either letting electricity through (ON, 1) or not (OFF, 0).\n\n"
      "Two states are very easy to tell apart, even when the electricity is a little noisy. "
      "That makes binary fast and reliable.\n\n"
      "By using lots of bits together, a computer can store any number. "
      "Eight bits together are called a byte.",
      "コンピューターのチップには「トランジスタ」という小さなスイッチが何十億個もつまっています。"
      "それぞれが電気を通す（ON・1）か、通さない（OFF・0）かのどちらかです。\n\n"
      "2つの状態なら、電気が少しみだれていても見分けるのがとてもかんたん。"
      "だから2進数は速くて、まちがいが少ないのです。\n\n"
      "ビットをたくさん並べれば、どんな数でも記録できます。8ビットのまとまりを「バイト」といいます。")),
    ("where",
     ("Where is binary used?", "2進数はどこで使われているの？"),
     ("Everywhere you see a screen!\n\n"
      "• Letters: the letter A is stored as 01000001.\n"
      "• Pictures: every dot (pixel) has its colour stored as numbers in binary.\n"
      "• Music and video: sounds are measured thousands of times a second and saved as binary numbers.\n"
      "• Phones, games, the internet, cars and even washing machines all send and save information as 0s and 1s.",
      "画面があるところなら、どこでも！\n\n"
      "・文字：「A」は 01000001 として記録されます。\n"
      "・写真：1つ1つの点（ピクセル）の色が2進数の数で記録されます。\n"
      "・音楽や動画：音を1秒間に何千回も測り、2進数の数として保存します。\n"
      "・スマホ、ゲーム、インターネット、車、せんたく機まで、情報を0と1で送ったり保存したりしています。")),
    ("important",
     ("Why is binary important?", "2進数はなぜ大切なの？"),
     ("Binary is the language that every digital device speaks. "
      "Knowing it helps you understand how computers really work on the inside.\n\n"
      "It is used by programmers, game makers, robot builders, scientists and engineers. "
      "Words like kilobyte, megabyte and gigabyte are all just counting bits and bytes.\n\n"
      "Once you can read binary, you are one step closer to building your own technology!",
      "2進数は、すべてのデジタル機器が話す「ことば」です。"
      "2進数がわかると、コンピューターの中で本当に何が起きているのかが見えてきます。\n\n"
      "プログラマー、ゲームクリエイター、ロボット開発者、科学者、エンジニアが使っています。"
      "キロバイト、メガバイト、ギガバイトという言葉も、ビットとバイトを数えているだけなのです。\n\n"
      "2進数が読めるようになれば、自分でテクノロジーを作る第一歩です！")),
    ("count",
     ("How to count in binary", "2進数で数えてみよう"),
     ("In decimal, when a place goes past 9 it goes back to 0 and the next place goes up by one (9 → 10).\n\n"
      "Binary works the same way, but a place can only go up to 1:\n"
      "0, 1, then 10 (two), 11 (three), 100 (four), 101 (five) ...\n\n"
      "Watch the switches count. The rightmost switch flicks every time. "
      "The next one flicks every 2 counts, the next every 4, and so on.",
      "10進数では、ある位が9をこえると0にもどり、となりの位が1つ上がります（9 → 10）。\n\n"
      "2進数も同じですが、1つの位は1までしか上がりません：\n"
      "0、1、そして 10（2）、11（3）、100（4）、101（5）…\n\n"
      "スイッチが数えるようすを見てみよう。一番右のスイッチは毎回切りかわります。"
      "そのとなりは2回に1回、その次は4回に1回…と続きます。")),
    ("place",
     ("Place values: always double", "位の数：いつも2倍"),
     ("In decimal each place is worth 10 times the place to its right: 1, 10, 100, 1000.\n\n"
      "In binary each place is worth 2 times the place to its right:\n"
      "1, 2, 4, 8, 16, 32, 64, 128 ...\n\n"
      "To read a binary number, add up the place values of the switches that are ON. "
      "1011 is 8 + 2 + 1 = 11.",
      "10進数では、それぞれの位は右どなりの10倍：1、10、100、1000。\n\n"
      "2進数では、それぞれの位は右どなりの2倍：\n"
      "1、2、4、8、16、32、64、128 …\n\n"
      "2進数を読むには、ONのスイッチの位の数をたし算します。"
      "1011 は 8 + 2 + 1 = 11 です。")),
    ("make",
     ("Make any number", "どんな数でも作れる"),
     ("Here is a method that works for every number:\n\n"
      "1. Find the biggest place value that is not bigger than your number. Turn that switch ON.\n"
      "2. Subtract it from your number.\n"
      "3. Repeat with what is left, moving right. If a place value is too big, leave it OFF.\n"
      "4. Stop when nothing is left.\n\n"
      "Watch the example: each step is shown on the right.",
      "どんな数にも使える方法があります：\n\n"
      "1. 作りたい数をこえない、一番大きい位の数を見つけて、そのスイッチをONにする。\n"
      "2. 作りたい数からその位の数をひく。\n"
      "3. 残りの数で、右へ進みながらくり返す。位の数が大きすぎたらOFFのまま。\n"
      "4. 残りが0になったら完成！\n\n"
      "右の例を見てみよう。1ステップずつ表示されます。")),
    ("try",
     ("Try it yourself", "自分でやってみよう"),
     ("Click the switches and watch the total change.\n\n"
      "Tips:\n"
      "• Odd numbers always have the 1 switch ON.\n"
      "• All switches ON makes one less than the next place value: 11111111 = 255.\n"
      "• Doubling a number moves every switch one place to the left.",
      "スイッチをクリックして、合計が変わるのを見てみよう。\n\n"
      "ヒント：\n"
      "・奇数（きすう）は、かならず「1」のスイッチがON。\n"
      "・全部ONにすると、次の位の数より1小さい数：11111111 = 255。\n"
      "・数を2倍にすると、すべてのスイッチが1つ左へずれます。")),
    ("howto",
     ("How to play BitFuse", "BitFuseの遊び方"),
     ("• A number appears at the top. Flick the switches so they make that number in binary.\n"
      "• Press IGNITE! The spark runs along the fuse through every switch. "
      "If you are right, the fireworks go off!\n"
      "• You have 99 seconds. Every second left is worth 100 points.\n"
      "• A wrong answer costs you a few seconds. If the time runs out, the game is over.\n"
      "• There are 100 levels. The numbers grow and the fireworks get bigger as you go.",
      "・上に数が表示されます。スイッチを切りかえて、その数を2進数で作ろう。\n"
      "・「点火！」を押すと、火花が導火線を走ってすべてのスイッチを通ります。"
      "正解なら花火が打ち上がる！\n"
      "・持ち時間は99秒。残り1秒につき100点です。\n"
      "・まちがえると数秒へります。時間がなくなるとゲームオーバー。\n"
      "・全部で100レベル。進むほど数が大きくなり、花火も大きくなります。")),
]


def lang():
    return LANG["current"]


def t(key, **fmt):
    en, ja = STRINGS[key]
    text = ja if lang() == "ja" else en
    return text.format(**fmt) if fmt else text


def both(key):
    return STRINGS[key]


def pick(pair):
    return pair[1] if lang() == "ja" else pair[0]
