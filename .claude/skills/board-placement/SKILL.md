---
name: board-placement
description: 基板の部品配置の案を、ユーザーがドラッグで動かして作れる図(2D の上から見た図と 3D、回して見られる)にして会話に出し、制約(外形・本体の壁・ねじ穴や取付穴からの距離・ブラケットの下の銅・高い部品と中のものの当たり・部品の重なり)をその場で OK / NG で見せる。ユーザーが「この配置で頼む」を押すと座標の文が返ってくるので、それを build_board.py に入れる。トリガー:「配置をいじりたい」「配置の案を出したい」「自分で動かしたい」「配置エディター」「部品の位置を決めたい」「ドラッグで」「3D で配置」「board-placement」。vein-base の基板(pcb/*/build_board.py)の配置を変えるときに使う。
---

# 基板の配置エディター

ユーザーが自分で部品を動かして配置の案を出すための図を、`show_widget`(visualize)で会話に出す。
ひな形は `editor.html`、基板ごとの中身は `configs/*.json`、組み立ては `make_widget.py`。

## 手順

1. 対象の基板の今の配置を数字で取る。`build_board.py` は最後に部品ごとのコートヤード
   (`REF (x, y) crtyd x .. y ..`)を出すので、手元の KiCad(Docker `vein-kicad:7`)で一度走らせて読む:
   ```sh
   docker run --rm -e HOME=/tmp -v $PWD:$PWD -w $PWD/pcb/<基板> vein-kicad:7 sh -c "python3 build_board.py dsn"
   ```
2. `configs/<基板>_<版>.json` を書く(既存の `configs/fp008_f13.json` を写して直す。書式は下)。
   部品ごとに `ext` = KiCad の回転 0° のときのコートヤード(原点からの x0, x1, y0, y1)、`r` = 置いている回転。
   まとまりで動かすもの(写したコア、ハブとそのまわり)は 1 つの箱にし、`note` にそう書く。
3. 図のコードを作って出す:
   ```sh
   python3 .claude/skills/board-placement/make_widget.py .claude/skills/board-placement/configs/<名前>.json > <scratchpad>/w.html
   ```
   出力をそのまま `mcp__visualize__show_widget` の `widget_code` に渡す(先に `mcp__visualize__read_me` を 1 回)。
   出す前に、`<script>` の中身を取り出して `node --check` で構文だけ確かめる。
4. ユーザーが「この配置で頼む」を押すと `〈title〉 の配置案: 上の端 y 33.0 / 穴 (0.0, 25.5) / J1 x 15.5 / U2 (15.5, 21.2, 90°) / …`
   が届く。数字を `build_board.py` の部品の位置に入れる(まとまりのものは原点と回転を足す関数で、例: fp008 の `hub()` と
   コアの `RP`)。config の値もその配置に更新して残す(次の案の出発点になる)。
5. 図の判定はコートヤードの箱どうしの目安。最後は `build_board.py` の assert と DRC、`build_3d.py` の干渉で確かめる。

ユーザーが画面のスクリーンショットだけを送ってきたときは、図の中の既知の 2 点(ねじ穴など)の間隔から mm に直して読む。

## config の書式

| キー | 中身 |
|---|---|
| `title` | 返ってくる文の頭 |
| `view` | 2D で見せる範囲(mm) |
| `sliders` | 変数(例: 上の端 `ye`)。`outline` の座標や `lockY` などに式で使える |
| `outline` | 基板の外形。点の列か `{"rrect": [x0, x1, y0, y1], "r": 下の角, "rtop": 上の角}`(y1 は式でもよい) |
| `body` | 基板の F 面の側にある本体(FP008 など)。`pts` / `depth`。F 面の部品は中なら壁から `rules.wall`、外なら `rules.outside` 離す |
| `zones` | `box` と `name`。`side: "B"` は B 面の部品の箱、`exposedOnly` は部品の `exposedB`(裏に出る銅、スルーホールの足)、`tallOnly` + `maxH` は高さ `h` が超える部品だけ。`z` があれば 3D でその深さの塊として描く |
| `keepouts` | 点(`x, y` か動く部品 `of`)から `r` 以内に部品を置かない |
| `customChecks` | JS の式。部品は id で(`M.y`, `J1.x`)、変数も使える。`value` は横に出す数 |
| `items` | 部品。`ext`, `x`, `y`, `r`, `h`(3D の高さ、F は基板の下へ)、`side`, `color`(purple / teal / gray / coral / blue)、`lockY`(式。左右だけ動く)、`edgeOpen`(この y より先は外形の判定から外す。口が端から出るコネクター)、`mustIn`(`body` / `out`)、`ghost`(破線で描く相手、例: 挿したプラグ)、`pin1`、`circle`(丸い穴。`rings` に半径 `r` の破線や対角 `hex` のナット)、`rotatable: false` |

## 気をつけること

- 3D は three.js r128(cdnjs)。読めないときは 2D だけで使える。3D では何もない所のドラッグで回転、ホイールで拡大。
- 回転はコートヤードの箱を 90° ずつ回すだけ。パッドの向き(1 番の位置)は `pin1` の赤い点で見せる。
- ユーザーが動かしたあとの値で判定が NG のまま送ってきたら、何が NG かを伝えてから実装するか聞く。
