# CLAUDE.md

M5Stack Atom VoiceS3R の下に積む 24×24 mm ベース(指静脈モジュール中継基板 + ケース)と、VoiceS3R・指静脈・NFC を 1 つに収める卓上筐体 Vein Station(`station/`、設計中)。KiCad / CadQuery をスクリプトで生成し、CI で製造データと 3D プレビューを出す。

Working guide for Claude Code sessions in this repo. Generated from
[ippoan/claude-md](https://github.com/ippoan/claude-md) `CLAUDE.md.template` —
edit shared parts there.

> **Org-wide rules** (issue→PR→push lifecycle, don't-assume-read-first,
> lib-first, branches/worktree, GitHub automation, secrets, never-do) live in
> `~/.claude/CLAUDE.md` (user memory, installed every session by ippoan/claude-md).
> Put **only repo-specific things** here; override the baseline only when needed
> (project memory wins).

## Read first

- [`README.md`](./README.md) — 構成、配線表、発注前の確認項目。
- 3D プレビュー: https://ippoan.github.io/vein-base/ (vein-base)、https://ippoan.github.io/vein-base/station/ (Vein Station)。main の CI が更新

## Repo-specific invariants

- 座標系: 原点 = Atom 中心(M2 ネジ)、+y = USB-C / PORT.A と反対側、基板の F 面が Atom 側。`build_pcb.py` / `build_case.py` / `build_viewer.py` の 3 本で共通。
- VoiceS3R の USB-C と PORT.A は同じ辺(−y)。J3 の差し込み口もこの辺に向ける。
- Ext.Pin の 2 列は **−y 端(y=−7.62)で揃う**。J1(x=+7.62)は +2.54 から 3V3,G5,G6,G7,G8、J2(x=−7.62)は 0 から G39,G38,5V,GND。実機の底面シルクで確認済み。ヘッダー位置を動かすときは基板・ケースのスロット・viewer の 3 か所を必ず一緒に直す。
- 版番号は `VERSION` だけで管理する。出力ファイル名(`vein_base_v<版>_*`)、Artifacts 名(`vein-base-v<版>-fab`)、基板裏シルクはここから入る。形状や配線を変えたら上げる。
- 生成物(STL / STEP / PDF / gerber zip / CPL)は git に入れない(`.gitignore` 済み)。古い生成物を発注しかけた事故があったため。取得は常に CI の Artifacts から。
- BOM の元データは `pcb/jlc_bom.csv`(LCSC 品番入り)。`fab/` は CI の出力先。
- フットプリントは lib nickname 付きで置き、`build_pcb.py` がプロジェクトローカルの `fp-lib-table` を書き出す(DRC の lib_footprint_* 警告対策)。標準から変えたフットプリントは `pcb/vein_base.pretty/` に置く(例: 2.4 mm の M2 穴)。
- `pcb/vein_base.kicad_pcb` は `build_pcb.py` の出力。手で編集せず、スクリプトを直す。

## Build / test / lint

ローカルに KiCad が無い前提。検証は PR の CI(`build` ジョブ)で行う。手元でできるのは構文チェックだけ:

```sh
python -c "import ast; [ast.parse(open(f, encoding='utf-8').read()) for f in ['pcb/build_pcb.py','case/build_case.py','tools/build_viewer.py','tools/make_jlc_cpl.py','station/build_station.py']]"
```

CI(`.github/workflows/build.yml`)の中身: `build_pcb.py` → kicad-cli で gerber / drill / pos / 原寸 PDF / STEP → `check_drc.py`(違反があれば fail)→ `build_case.py` → `build_viewer.py`(ケースと部品・VoiceS3R の干渉が 0.01 mm³ を超えたら fail)→ `station/build_station.py`(筐体とモジュール・プラグ・ケーブルの干渉で fail)。DRC の違反と干渉チェックの失敗は設計の問題なので、スクリプト側で握りつぶさない。

## CI / auto-merge (repo-specific config)

Common auto-merge / `Refs #N` rules are in user memory. Only repo-specific values here:

- `auto-merge.yml` が `ippoan/ci-workflows` の reusable を `secrets: inherit` で呼ぶ。
- Required status checks (`main` branch protection):
  ```
  build
  ```
- PR を別ブランチの上に積む(stacked PR)と、ベースが main に付け替わった後に ready にしても auto-merge が起動しなかった。PR は main 向けに作る。

## Vein Station(`station/`)

`station/build_station.py` 1 本で、筐体(`shell` = 天板+壁、`lid` = 底蓋+台)の STEP / STL と `site/station/` の 3D プレビューを作る。変更のたびに `REV`(r1, r2, …)を上げ、1 変更 1 PR で出す。

- 座標: x = 左→右、`ys` = 奥→手前(3D では Y = −ys)、z = 天面 0 で下向きが負。上面図(artifact のたたき台)と同じ数値で書く。
- 配置(r9): 左端に NFC を縦置き(Grove 端子は手前)、その右の上段に指静脈、下段に VoiceS3R。VoiceS3R の USB-C / PORT.A / J3 の辺は右のケーブル置き場に向け、USB ケーブルは右の壁の下端から出す。外形 91 × 63 × 27.6。
- 固定方法はどのモジュールも同じ: 底蓋の台で下から押し上げ、天板の返しに当て、天板から垂らした短い枠(縁取り)で横を固定。モジュールにネジは使わない。
  - 上面を全部開けると上に抜けるので、VoiceS3R も返し(1.2)で押さえる。そのまわりだけ天板を 0.8 に薄くして、沈み込みを抑える。
  - 枠は折れないように短くする(天板下面から 2.25〜5.25)。
- vein-base はケースを使わず基板だけ入れる。基板は Ext.Pin に挿さったまま、底蓋のレール(ピンヘッダーの足をよける)と中央ボス(J3 をよける)で VoiceS3R ごと押し上げる。基板の配置は `board()` で vein-base の基板座標から変換する。
- 底蓋: 左端は爪、M3 × 3 を三角配置(手前左・奥の中ほど・右手前)。
- 実測値(写真から、±1〜2):
  - VoiceS3R の側面は、下から PORT.A(Grove、底面から 0〜4)→ USB-C(その上)。上面ボタン・スピーカー穴は縁から 3 内側。
  - USB ケーブルはサンワ KU-CCP100KAW18BK(回転コネクタ)。L字にした頭は側面から 14、金属円筒 ⌀9、ケーブル ⌀3.5。
  - NFC Unit は 48 × 23.5 × 8、Grove は短辺の中央、アンテナは表(「NFC」ラベル面)、裏にネジ頭 1(Grove 端から 12、幅の中央)。
  - NFC → PORT.A の Grove は約 8 cm 必要(10 cm か手持ちの 20 cm を置き場にたたむ)。
- 指静脈モジュールは採寸待ちで、59 × 26 × 15 の仮の箱。コネクタ位置と J3 からの経路は未確定。
- 干渉チェックは筐体とモジュール・プラグ・ケーブルの間だけ。プラグ同士の重なりは参考形状なので検査しない。

## 発注と原寸確認

- 原寸確認は `vein_base_v<版>_fitcheck_1to1_seen_from_below.pdf` を 100% で印刷し、**回さずに**「USB-C / cable side」を PORT.A 側に向けて VoiceS3R 底面に当てる。`fitcheck_1to1.pdf`(上から見た図)を回して当てると、見かけ上合ってしまう。
- 基板と実装は JLCPCB の Standard PCBA。SMT は Bottom 面(J3)、J1/J2 は THT 実装。実装プレビューで、J3 が裏面にあって開口が USB-C 側を向いているか確認する。
- ケースは MJF PA12。国内なら DMM.make、基板と同じ荷物にするなら JLC3DP(JLCPCB のカートでまとめられる)。
- 決済・ログインは人が行う。Claude はファイルの用意と確認まで。

---

_Generated from [ippoan/claude-md](https://github.com/ippoan/claude-md)
`CLAUDE.md.template`; the org baseline lives in user memory (`~/.claude/CLAUDE.md`,
installed by install.sh). Edit shared rules in `user-memory.md` / this template._
