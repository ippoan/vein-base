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
- VoiceS3R の USB-C と PORT.A は同じ辺(−y)。J3 は高さ 3.4 でヘッダー樹脂のすき間 2.54 に入らないので、基板を +y へ Atom の外まで伸ばし、表面(F)の Atom の外に置いて差し込み口を +y 端に向ける(USB-C / PORT.A のプラグを避ける)。
- Ext.Pin の 2 列は **−y 端(y=−7.62)で揃う**。J1(x=+7.62)は +2.54 から 3V3,G5,G6,G7,G8、J2(x=−7.62)は 0 から G39,G38,5V,GND。実機の底面シルクで確認済み。ヘッダー位置を動かすときは基板・ケースのスロット・viewer の 3 か所を必ず一緒に直す。
- 版番号は `VERSION` だけで管理する。出力ファイル名(`vein_base_v<版>_*`)、Artifacts 名(`vein-base-v<版>-fab`)、基板裏シルクはここから入る。形状や配線を変えたら上げる。
- 生成物(STL / STEP / PDF / gerber zip / CPL)は git に入れない(`.gitignore` 済み)。古い生成物を発注しかけた事故があったため。取得は常に CI の Artifacts から。
- BOM の元データは vein-base が `pcb/jlc_bom.csv`、station 基板が `pcb/station_board/jlc_bom.csv`、指静脈 Unit の基板が `pcb/vein_unit_board/jlc_bom.csv`(どれも LCSC 品番入り)。`fab/` は CI の出力先。
- フットプリントは lib nickname 付きで置き、`build_pcb.py` がプロジェクトローカルの `fp-lib-table` を書き出す(DRC の lib_footprint_* 警告対策)。標準から変えたフットプリントは `pcb/vein_base.pretty/` に置く(例: 2.4 mm の M2 穴)。
- `pcb/vein_base.kicad_pcb` は `build_pcb.py` の出力。手で編集せず、スクリプトを直す。

## Build / test / lint

ローカルに KiCad が無い前提。検証は PR の CI(`build` ジョブ)で行う。手元でできるのは構文チェックだけ:

```sh
python -c "import ast; [ast.parse(open(f, encoding='utf-8').read()) for f in ['pcb/build_pcb.py','pcb/station_board/build_board.py','case/build_case.py','tools/build_viewer.py','tools/make_jlc_cpl.py','station/build_station.py']]"
```

CI(`.github/workflows/build.yml`)の中身: `build_pcb.py` → kicad-cli で gerber / drill / pos / 原寸 PDF / STEP → `check_drc.py`(違反があれば fail)→ 同様に `pcb/station_board/build_board.py` から station 基板の gerber / drill / pos / CPL / DRC(`silk_edge_clearance` はこの基板だけ無視)→ `build_case.py` → `build_viewer.py`(ケースと部品・VoiceS3R の干渉が 0.01 mm³ を超えたら fail)→ `station/build_station.py`(筐体とモジュール・プラグ・ケーブルの干渉で fail)。DRC の違反と干渉チェックの失敗は設計の問題なので、スクリプト側で握りつぶさない。

## CI / auto-merge (repo-specific config)

Common auto-merge / `Refs #N` rules are in user memory. Only repo-specific values here:

- `auto-merge.yml` が `ippoan/ci-workflows` の reusable を `secrets: inherit` で呼ぶ。
- Required status checks (`main` branch protection):
  ```
  build
  ```
- PR を別ブランチの上に積む(stacked PR)と、ベースが main に付け替わった後に ready にしても auto-merge が起動しなかった。PR は main 向けに作る。

## Vein Station(`station/`)

`station/build_station.py` 1 本で、筐体(`shell` = 天板+壁、`lid` = 底蓋+台)の STEP / STL と `site/station/` の 3D プレビューを作る。変更のたびに `REV`(r1, r2, …)を上げ、1 変更 1 PR で出す。基板は `pcb/station_board/`(r12、`build_board.py`)が生成する 60 × 35 mm の 1 枚基板で、VoiceS3R の Ext.Pin・指静脈 J3(G5/G6)・MAX3232(G7=送信 / G8=受信)・DIP(1+2 = Passthrough、3+4 = Cross)・DB9 オス RA をまとめ、接続口はすべて奥の壁に出す。同じ回路・同じ配線で外形を広げた版(`build_board.py pf` → `station_board_pf`、92 × 71)は、既製ケースタカチ PF13-4-9 用(印刷部品なし)。基板はケースに元からある基板用ボス(87 × 47)にタカチ TPS-M2.3-7 と M2.3 ねじで留め、モジュールは M3 オスメス六角スペーサーとナットで基板に立てる。60 × 35 の範囲と配線は共通。ケース側は `station/build_station_pf.py`(ケースはタカチ公式 STP の実測値からの簡略形状、STP は入れない)が、干渉チェック・3D プレビュー(`site/station-pf/`)・タカチの穴加工に出す DXF と手加工用の原寸型紙 PDF(A4、どちらも天板の窓 2 つだけ、Pages の site/station-pf/ から取れる)を作る。接続口はすべて背面なので背面パネルは付けない。基板の穴(H1..H8、B1..B4)はこのスクリプトと `build_board.py` の 2 か所にあるので一緒に直す。正本は `build_board.py` / `build_station.py` の docstring。

- 指静脈 Unit(`station/build_vein_unit.py cs|sic`、`site/vein-unit-cs/`・`site/vein-unit-sic/`、REV vu3〜): 指静脈モジュールだけを小さいタカチのケースに入れ、Grove 1 本(5V → LDO で 3.3V)で PortABC の PORT.C につなぐ案。机に並べて使う想定。`cs` = CS75N-B(35 × 75 × 12、ねじの柱の間にはめ込み、端のすき間で線を直付け)、`sic` = SIC5-9-2B(45 × 90 × 20、中いっぱいの基板を M2 ボス 4 本に留め、その上に指静脈、基板に Grove ソケット・LDO、付属ケーブル④(9P → 4P)の 9P 側の端子を 3〜6 に差し替え、指静脈の脇の真ん中の横向き J1(53261-0471)へまっすぐ挿す)。基板は `pcb/vein_unit_board/build_board.py`(u3、78 × 39、M2 × 4、配線もスクリプトに直書き、CI で gerber / CPL / DRC → `fab/vein_unit/`)。指静脈の位置(y −16.5〜9.5)と J1 の位置は 3D と基板の 2 か所にあるので一緒に直す。ケースはタカチ STP の実測値からの簡略形状(STP は入れない)。付属ケーブルは平らな窓の側の端面から水平に出る MX1.25 9P、反対側はデュポン。box ヘルパー・指静脈のイメージ形状・ページ出力は `station/shapes.py`(PF と共有)。
- 座標: x = 左→右、`ys` = 奥→手前(3D では Y = −ys)、z = 天面 0 で下向きが負。上面図(artifact のたたき台)と同じ数値で書く。
- 配置(r9): 左端に NFC を縦置き(Grove 端子は手前)、その右の上段に指静脈、下段に VoiceS3R。VoiceS3R の USB-C / PORT.A / J3 の辺は右のケーブル置き場に向け、USB ケーブルは右の壁の下端から出す。外形 91 × 63 × 27.6。
- 固定方法はどのモジュールも同じ: 底蓋の台で下から押し上げ、天板の返しに当て、天板から垂らした短い枠(縁取り)で横を固定。モジュールにネジは使わない。
  - 上面を全部開けると上に抜けるので、VoiceS3R も返し(1.2)で押さえる。そのまわりだけ天板を 0.8 に薄くして、沈み込みを抑える。
  - 枠は折れないように短くする(天板下面から 2.25〜5.25)。
- vein-base はケースを使わず基板だけ入れる。基板は Ext.Pin に挿さったまま、底蓋のレール(ピンヘッダーの足をよける)と中央ボス(J3 をよける)で VoiceS3R ごと押し上げる。基板の配置は `board()` で vein-base の基板座標から変換する。
- 底蓋: 左端は爪、M3 × 3 を三角配置(手前左・奥の中ほど・右手前)。
- 寸法(外形は公式値、細部は写真から ±1〜2):
  - VoiceS3R(24 × 24 × 16.8)と NFC の外形は M5Stack 公式 STL: https://github.com/m5stack/M5_Hardware/blob/a240115c94b19ecf647f229c47fa9a8ce46ccdc4/Products/C126-ECHO_Atom_VoiceS3R/Structures/Atom_VoiceS3R.stl / https://github.com/m5stack/M5_Hardware/blob/a240115c94b19ecf647f229c47fa9a8ce46ccdc4/Products/U216_Unit_NFC/Structures/Unit_NFC.stl (MIT)。
  - VoiceS3R の側面は、下から PORT.A(Grove、底面から 0〜4)→ USB-C(その上)。上面ボタン・スピーカー穴は縁から 3 内側。
  - USB ケーブルはサンワ KU-CCP100KAW18BK(回転コネクタ)。L字にした頭は側面から 14、金属円筒 ⌀9、ケーブル ⌀3.5。
  - NFC Unit は 48 × 24 × 8 (公式 STL)、Grove は短辺の中央、アンテナは表(「NFC」ラベル面)、裏にネジ頭 1(Grove 端から 12、幅の中央)。
  - NFC → PORT.A の Grove は約 8 cm 必要(10 cm か手持ちの 20 cm を置き場にたたむ)。
- 指静脈モジュールの外形は公式値 59 × 26 × 15 (取付厚 13.5、Waveshare 製品ページ https://www.waveshare.com/finger-vein-scanner-module-a.htm)。コネクタ位置と J3 からの経路は未確定。
- 干渉チェックは筐体とモジュール・プラグ・ケーブルの間だけ。プラグ同士の重なりは参考形状なので検査しない。

## 発注と原寸確認

- 原寸確認は `vein_base_v<版>_fitcheck_1to1_seen_from_below.pdf` を 100% で印刷し、**回さずに**「USB-C / cable side」を PORT.A 側に向けて VoiceS3R 底面に当てる。`fitcheck_1to1.pdf`(上から見た図)を回して当てると、見かけ上合ってしまう。
- 基板と実装は JLCPCB の Economic PCBA(片面のみ対応)。全部品(J1/J2 = THT、J3 = SMD)が Top 面にあり、1 回で付く。自分ではんだ付けする部品は無い。実装プレビューで、J3 が表面にあって開口が +y 端(USB-C と反対)を向いているか確認する。
- ケースの本番材料は DMM.make の「PA12｜MJF」(グレー、磨きなし)。形の確認だけなら SLA のエコノミーレジンでよい(肉厚は 1.0 mm 以上)。基板と同じ荷物にするなら JLC3DP の MJF PA12(JLCPCB のカートでまとめられる)。
- 決済・ログインは人が行う。Claude はファイルの用意と確認まで。

---

_Generated from [ippoan/claude-md](https://github.com/ippoan/claude-md)
`CLAUDE.md.template`; the org baseline lives in user memory (`~/.claude/CLAUDE.md`,
installed by install.sh). Edit shared rules in `user-memory.md` / this template._
