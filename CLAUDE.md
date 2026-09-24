# CLAUDE.md

M5Stack Atom VoiceS3R の下に積む 24×24 mm ベース(指静脈モジュール中継基板 + ケース)。KiCad / CadQuery をスクリプトで生成し、CI で製造データと 3D プレビューを出す。

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
- 3D プレビュー: https://ippoan.github.io/vein-base/ (main の CI が更新)

## Repo-specific invariants

- 座標系: 原点 = Atom 中心(M2 ネジ)、+y = USB-C / PORT.A と反対側、基板の F 面が Atom 側。`build_pcb.py` / `build_case.py` / `build_viewer.py` の 3 本で共通。
- VoiceS3R の USB-C と PORT.A は同じ辺(−y)。J3 の差し込み口もこの辺に向ける。
- Ext.Pin の 2 列は **−y 端(y=−7.62)で揃う**。J1(x=+7.62)は +2.54 から 3V3,G5,G6,G7,G8、J2(x=−7.62)は 0 から G39,G38,5V,GND。実機の底面シルクで確認済み。ヘッダー位置を動かすときは基板・ケースのスロット・viewer の 3 か所を必ず一緒に直す。
- 版番号は `VERSION` だけで管理する。出力ファイル名(`vein_base_v<版>_*`)、Artifacts 名(`vein-base-v<版>-fab`)、基板裏シルクはここから入る。形状や配線を変えたら上げる。
- 生成物(STL / STEP / PDF / gerber zip / CPL)は git に入れない(`.gitignore` 済み)。古い生成物を発注しかけた事故があったため。取得は常に CI の Artifacts から。
- BOM の元データは `pcb/jlc_bom.csv`(LCSC 品番入り)。`fab/` は CI の出力先。
- フットプリントは lib nickname 付きで置き、`build_pcb.py` がプロジェクトローカルの `fp-lib-table` を書き出す(DRC の lib_footprint_* 警告対策)。標準から変えたフットプリントは `pcb/vein_base.pretty/` に置く(例: 2.4 mm の M2 穴)。
- `station/` は一体筐体 Vein Station の案(版は `build_station.py` の `REV`)。vein-base はケースを使わず基板だけを入れる(底蓋のレールとボスで基板ごと VoiceS3R を返しに押し上げる)。モジュール寸法は写真からの実測で ±1〜2 mm、指静脈モジュールは仮の箱。筐体とモジュール・プラグ・ケーブルの干渉は CI で fail させる(プラグ同士の重なりは参考形状なので検査しない)。
- `pcb/vein_base.kicad_pcb` は `build_pcb.py` の出力。手で編集せず、スクリプトを直す。

## Build / test / lint

ローカルに KiCad が無い前提。検証は PR の CI(`build` ジョブ)で行う。手元でできるのは構文チェックだけ:

```sh
python -c "import ast; [ast.parse(open(f, encoding='utf-8').read()) for f in ['pcb/build_pcb.py','case/build_case.py','tools/build_viewer.py','tools/make_jlc_cpl.py']]"
```

CI(`.github/workflows/build.yml`)の中身: `build_pcb.py` → kicad-cli で gerber / drill / pos / 原寸 PDF / STEP → `check_drc.py`(違反があれば fail)→ `build_case.py` → `build_viewer.py`(ケースと部品・VoiceS3R の干渉が 0.01 mm³ を超えたら fail)。DRC の違反と干渉チェックの失敗は設計の問題なので、スクリプト側で握りつぶさない。

## CI / auto-merge (repo-specific config)

Common auto-merge / `Refs #N` rules are in user memory. Only repo-specific values here:

- `auto-merge.yml` が `ippoan/ci-workflows` の reusable を `secrets: inherit` で呼ぶ。
- Required status checks (`main` branch protection):
  ```
  build
  ```
- PR を別ブランチの上に積む(stacked PR)と、ベースが main に付け替わった後に ready にしても auto-merge が起動しなかった。PR は main 向けに作る。

## 発注と原寸確認

- 原寸確認は `vein_base_v<版>_fitcheck_1to1_seen_from_below.pdf` を 100% で印刷し、**回さずに**「USB-C / cable side」を PORT.A 側に向けて VoiceS3R 底面に当てる。`fitcheck_1to1.pdf`(上から見た図)を回して当てると、見かけ上合ってしまう。
- 基板と実装は JLCPCB の Standard PCBA。SMT は Bottom 面(J3)、J1/J2 は THT 実装。実装プレビューで、J3 が裏面にあって開口が USB-C 側を向いているか確認する。
- ケースは MJF PA12。国内なら DMM.make、基板と同じ荷物にするなら JLC3DP(JLCPCB のカートでまとめられる)。
- 決済・ログインは人が行う。Claude はファイルの用意と確認まで。

---

_Generated from [ippoan/claude-md](https://github.com/ippoan/claude-md)
`CLAUDE.md.template`; the org baseline lives in user memory (`~/.claude/CLAUDE.md`,
installed by install.sh). Edit shared rules in `user-memory.md` / this template._
