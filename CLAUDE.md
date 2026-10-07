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
python -c "import ast; [ast.parse(open(f, encoding='utf-8').read()) for f in ['pcb/build_pcb.py','pcb/station_board/build_board.py','pcb/station_esp_board/build_board.py','pcb/kicad_ses.py','case/build_case.py','tools/build_viewer.py','tools/make_jlc_cpl.py','station/build_station.py','station/build_station_sw.py','station/build_station_sw75.py','station/build_station_sw130.py','station/build_station_print.py','station/build_vein_unit_print.py','station/shapes.py','pcb/vein_unit_board/build_board.py']]"
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

`station/build_station.py` 1 本で、筐体(`shell` = 天板+壁、`lid` = 底蓋+台)の STEP / STL と `site/station/` の 3D プレビューを作る。変更のたびに `REV`(r1, r2, …)を上げ、1 変更 1 PR で出す。基板は `pcb/station_board/`(r12、`build_board.py`)が生成する 60 × 35 mm の 1 枚基板で、VoiceS3R の Ext.Pin・指静脈 J3(G5/G6)・MAX3232(G7=送信 / G8=受信)・DIP(1+2 = Passthrough、3+4 = Cross)・DB9 オス RA をまとめ、接続口はすべて奥の壁に出す。同じ回路・同じ配線で外形を広げた版(`build_board.py pf` → `station_board_pf`、92 × 71)は、既製ケースタカチ PF13-4-9 用(印刷部品なし)。基板はケースに元からある基板用ボス(87 × 47)にタカチ TPS-M2.3-7 と M2.3 ねじで留め、モジュールは M3 オスメス六角スペーサーとナットで基板に立てる。60 × 35 の範囲と配線は共通。ケース側は `station/build_station_pf.py`(ケースはタカチ公式 STP の実測値からの簡略形状、STP は入れない)が、干渉チェック・3D プレビュー(`site/station-pf/`)・タカチの穴加工に出す寸法入りの加工図(DXF / PDF、窓の中心をケース中心からの寸法で入れる)と手加工用の原寸型紙 PDF(A4、どちらも天板の窓 2 つだけ、Pages の site/station-pf/ から取れる)を作る。接続口はすべて背面なので背面パネルは付けない。基板の穴(H1..H8、B1..B4)はこのスクリプトと `build_board.py` の 2 か所にあるので一緒に直す。正本は `build_board.py` / `build_station.py` の docstring。

- 実機テスト済み(2026-10-01、station 基板 r10 + VoiceS3R): RS232 は SW1 1+2 ON(Passthrough)で FC-1200B と双方向に通り、測定値まで取れた(G7 = 送信 / G8 = 受信、9600 8N1)。ファームは ippoan/alc-app-s3 の `atoms3-timecard` の `station` feature 版で、Pages の `firmware/alc-hub-atoms3-timecard-station-merged.bin` を `espflash write-bin 0x0` で焼く(Pages の `timecard.html` のボタンは LAN あり版なので使わない)。未確認: 指静脈(J3、`vein` feature 版が要る)、NFC、SW1 の Cross。
- シルクの文字は基板の外にはみ出しても CI では落ちない(station 基板は DB9 の外形シルクのため `silk_edge_clearance` を無視している)。届いた r10 では SW1 の説明 1 行(33 文字、幅 26.4)の先頭 `SW1 1+2 ` が −x 端の外に切れ、残りに SW1 のリファレンスが重なっていた。文字は中央揃えで 1 文字 ≒ 0.8 × size の幅なので、足すときは両端が外形に入るか計算する。r12b(60 × 35 / PF / SW75)で 2 行(`1+2 ON = PASS` / `3+4 ON = CROSS`)に分けた。SW130 は発注済みなので `SW1 12=PASS 34=CROSS` のまま。
- ESP 基板(`pcb/station_esp_board/build_board.py`、e1。`sw` 引数で SW-85B 用 52 × 76、配置は `POS` 表で上書き): PF 用 station 基板の外形・穴・DB9 / MAX3232 / DIP / J3 の位置はそのままで、VoiceS3R の代わりにその回路(ESP32-S3-WROOM-1、USB-C、AMS1117、ES8311、MEMS マイク、NS4150B、SMD スピーカー)を載せた版。GPIO は VoiceS3R と同じ。Grove は J6 = NFC(G2/G1)と J7 = 予備(G38/G39)。配線は freerouting 2.4.1 の `.ses`(`build_board.py dsn` → freerouting → `.ses`)。GND は両面のベタで取り、スクリプトがスティッチングビアと、ビアの無い島へのビアを足す。ES8311(0.4 ピッチ)のため線幅 0.2 / クリアランス 0.15(5V だけ 0.5)。穴・ボスの座標は `station_board` と同じなので一緒に直す。`.ses` の読み込みは `pcb/kicad_ses.py`(station_board と共有)。
- SW75 案(`station/build_station_sw75.py`、REV sw75g、`site/station-sw75/`): 最小案。指静脈と DB9 をタカチ SW-75B(内寸 42.8 × 67.8 × 23、壁の勾配はロフトで表現)に入れ、VoiceS3R はケースの外に置く。基板は station 基板の `sw75` 外形(`pcb/station_board/build_board.py sw75`、回路・部品・BOM は station 基板と同じ、配置と配線 `station_board_sw75.ses` だけ別)で、ケースいっぱい(40.8 × 68.1)+ +y の端面から出る幅 26 の舌。VoiceS3R は舌の上に J1 / J2(普通のピンヘッダー)で立ち、USB-C / PORT.A は外(+y)、上面はカバーと同じ高さ。NFC は VoiceS3R の PORT.A。部品は全部上面(片面、Economic)。MAX3232 と J3 は指静脈の下、SW1 は DB9 の上(カバーを外して切り替え)。舌の下は H5 の足(M3 × 8 メスメス + ゴム足)で机に当てる。基板は指静脈の M3 × 6 スペーサーで保持(H1 / H4 は床の ASR-7 へ)。J3 は指静脈のソケットの真下で口を同じ -y に向ける(ケーブルが S 字に折り返さず C 字 1 回で入る。反対向きは取り回しが悪いとユーザー指摘)。基板の -y 端に切り欠き(`NOTCH`)があり、ケーブルの余りを基板の下へ逃がす。切り欠きは DSN に入れていない。穴・部品の位置は `build_board.py` の `sw75` と同じ値を持つので一緒に直す。加工はカバー(指静脈の窓)、+x の側面(DB9)、+y の端面(舌)の 3 面で、DB9 と舌の切り欠きはボディの上縁まで開いていて基板を上から落とし込む。口の寸法は定数(`VEIN_WIN` / `DB9_CUT` / `TONGUE_CUT`)にあり、3D の穴と図の両方がそれを使う。3 面の寸法入り加工図(DXF + PDF、側面・端面の高さは床の外面から)と A4 原寸の型紙 1 枚をページから取れる。sw75e までの ESP 基板 sw75(`pcb/station_esp_board` の `sw75`、VoiceS3R の回路を基板に載せた版)は、WROOM とマイクが JLC で Standard PCBA 限定で費用が高く、BLE を使うので技適の無いチップ直載せもできないため、この形に切り替えた(基板のスクリプトと CI の出力は残している)。
- SW130 案(`station/build_station_sw130.py`、REV sw130l、`site/station-sw130/`): 細い案。タカチ SW-130B(40 × 25 × 130、内寸 35.5 × 17 × 125.5、17〜20 はカバーの縁で 32.8 × 122.8、ボス・リブなし)に、−y から DB9 → DIP(+x 側)と指静脈のケーブル → 指静脈(下に MAX3232)→ VoiceS3R を一列に全部入れる。基板は station 基板の `sw130` 外形(`build_board.py sw130`、34.8 × 122.7、片面、BOM は `jlc_bom_sw130.csv`)を床から M3 × 3 で浮かせる(部材はマルツ: 床は ASB-303E を VHB 5952(厚さ 1.14)で床に貼る、H1..H4 は座金 WN-5(1.0)+ BSB-305E のオスを基板に通して床のスペーサーへ、H5..H7 は M3 × 4 バインドねじ。5 mm の床は VHB の厚みで DB9 がカバーに当たるので不可)。VoiceS3R は中央で J1 / J2 に立ち、カバーの窓から 2.5 出る。USB-C は +y の端面(その下の PORT.A も同じ幅 10.6 の切り欠きから挿せる、予備。切り欠きは DB9 と同じくボディの上縁まで開ける)、リセット(ポート面の左隣の側面の U 字の板、公式 STL で確認、硬い)は +x の側面の幅 6 の切り欠き(底面から 11.7 より上をボディの上縁まで開ける。6 × 8 の穴だと上端がボディの上縁を 0.2 越えてカバーにかかるので sw130j で切り欠きにした)からドライバーで押す。NFC は VoiceS3R の PORT.A を使わず、基板の Grove J6(+x の側面、VoiceS3R の手前の (10.65, 30.8)。リセットと同じ切り欠きから挿す)を G38 = SDA / G39 = SCL(4.7k プルアップ)で使う(NFC と USB を別の面に出すため。ファームで I2C をこのピンで開く)。J6 は縁から 2.3 内側、高さ 6 で指静脈の下面(基板から 7.2)の下に入る。sw130k(基板 v0.17、シルク r12c)で J6 を −x の側面(DB9 の近く、(−10.65, −45))から +x へ移し、加工を 5 面から 4 面(カバー・+x 側面・両端面)に減らした。sw130l(基板 v0.18、シルク r12d)で J6 を VoiceS3R の手前(y 30.8)まで寄せ、+x の側面の Grove の穴とリセットの切り欠きを 1 つの切り欠き(`SIDE_CUT`、幅 23.7、底面から 7.9 より上をボディの上縁まで、底の角 R1)にまとめた。最初の 4 台(sw130j、基板 v0.15)は −x のまま発注した(2026-10-05、マルツ経由でタカチ、単価 ¥6,045。1 面だけの PF13 は ¥2,315 で、面の数が効いているとみた)。部品は当初 JLC の HY2.0(C722729)だったが、ピンがパッドに合わないと JLC から指摘があり、フットプリントどおりの JST S4B-PH-SM4-TB(LF)(SN)(C265102)に替えた(sw130h。本体の前端は縁から 2.3 内側で、Grove のプラグは側面の穴から差し込む。PH のソケットに Grove のプラグは挿さるがロックはかからない)。Grove の穴(`GROVE_CUT`、HY2.0 の本体 12 × 6 が入る 12.6 × 6.7)は sw130l から `SIDE_CUT` の一部。R0.5 は避ける(タカチの資料で R0.5 は細い刃物で遅く、加工代が上がる)。指静脈のケーブルは MX1.25 4P・約 10 cm(5 cm は在庫なし)で、ソケットから J3 まで C 字に 1 回折り返し(約 3 cm)、余り約 7 cm は 18 mm で 4 本並べて指静脈の手前の −x 側に置く(干渉チェックに入れている。ケースにケーブルの穴は無い)。そのために指静脈を VoiceS3R 側へ 8 寄せ(y −30〜29、H1..H4 の M3 × 5 に VHB で貼るのでねじ穴は関係ない)、SW1(DIP)を指静脈と DB9 の間の +x 側(11.3, −44.3)に移し、H7 を (14, −34) に動かした(基板 v0.15、シルクは r12b)。DB9 の上端(18.2)とプラグのフード(19.0)がボディの上縁(17、底面から 19.5)を越えるので、カバーの −y 端面の縁(高さ 3)を DB9 の切り欠きと同じ幅 31.3 で天板の裏まで切り取る(`COVER_DB9` / `DB9_FILE`。sw130i までは注記だけ「1.4 削る」で、3D と DXF は天板の裏まで切っていた)。USB-C の金属部の上端(17.2)もボディの上縁を越えるので、カバーの +y 端の縁を USB の切り欠きの幅だけ 0.5 削る(`COVER_USB`)。指静脈はカバーから 5.4 出る。穴・部品の位置は `build_board.py` の `sw130` と同じ値を持つので一緒に直す。加工図(カバー・+x 側面・両端面、合わせ目 19.5 を破線で入れる)と A4 原寸の型紙、タカチへの見積もり依頼に付ける加工位置図(`vein_station_<REV>_positions.pdf`、A4 横 1 枚・日本語、4 面を外形の端からの連続寸法で、ボディの加工は赤・カバーの縁の逃がしは青。`station/position_sheet.py`、CI に IPAex ゴシックを入れている)をページから取れる。タカチには自前の座標(±x / ±y)の DXF だけでは伝わらず、タカチの図面基準で位置を聞き返された(2026-10-01)。
- 3D 印刷 A に決定(2026-10-05): 基板は `pcb/station_board/build_board.py print_a`(34.4 × 115.95、回路・部品・BOM は sw130 と同じ `jlc_bom_sw130.csv`、配線 `station_board_print_a.ses`、CI で `fab/station_print_a/`)。DB9(−y)の後ろに SW1(−x)と J6(+x、口は +x の側面)を並べ、その後ろに J3(口は −y、プラグは SW1 と J6 の間)。指静脈(y −25.4〜33.6)は床から立てた柱 4 本(基板の 4.3 の穴 P1..P4 を通す)に VHB で載せ、その下に MAX3232・C1〜C5・R1 / R2(すき間 2.9)。VoiceS3R は +y の端(J1 / J2)。基板は床のボスに M2 タッピング(H1..H5)。部品の位置は `build_station_print.py` の `concept_a()` と同じ値を持つので一緒に直す。外形 38.6 × 119.9 × 16.5。B の基板は `build_board.py print_b`(46.35 × 63.1 + VoiceS3R の角、指静脈の台(左の棚・手前の横木)を避けた L 字、ふたの受けの 3 か所と右奥の角を切り欠く(`NOTCHES` = `concept_b` の `NOTCHES_B`)、VoiceS3R は指静脈の 0.5 横、VoiceS3R の角は箱の外面まで出る。回路・部品・BOM は同じ `jlc_bom_sw130.csv`、配線 `station_board_print_b.ses`、CI で `fab/station_print_b/`)。VoiceS3R は 90° 回して USB-C を +x(J1 は y = AY + 7.62、J2 は AY − 7.62)、DB9 はその後ろの +x の縁(右の側面、ふたの下)、指静脈は基板から 3.9 上の台(本体と一体: 左の壁の棚・手前の横木・右奥の柱 1 本(基板の 3.2 の穴 P1 を通す))に載せ、その下に MAX3232・C1〜C5・R1 / R2・SW1(ふたと指静脈を外して切り替え)・J3(ソケットの端の下、口は +y、横型。縦型は指静脈の下では 7.5 になって不利)とケーブルの余り。J6 は DB9 の後ろの奥の縁で口は奥(+x の側面だと 3 本目の受けが置けない)。2026-10-07 にユーザー案(指静脈を低い部品の上に浮かせて面積を減らす)で配置と配線を作り直した(freerouting 2.4.1)。M2 タッピング(H1..H4)。部品の位置は `concept_b()` と同じ値を持つので一緒に直す。
- 3D 印刷の試作(`station/build_station_print.py`、`site/station-print-a/`・`site/station-print-b/`): タカチの加工(SW-130B の 5 面加工で 1 台 ¥6,045)の代わりに、箱を MJF PA12 で造形し、基板も箱に合わせて作り直す前提の試作(配置だけ、基板は未配線)。A = 一列(38.6 × 119.9 × 16.5、MAX3232 と C1〜C5 は指静脈の下の枠の内側)、B = 2 列(52.8 × 70.3 × 23.6、2026-10-07 に 52.8 × 79.1 × 16.7 から。指静脈は左手前で台の上、VoiceS3R は右手前で USB-C は右・リセットは手前。VoiceS3R の角は M5Stack ATOMIC のように壁もふたもなく、右と手前の面は箱の面とそろい、基板と床がその下まで出る。ピンヘッダーだけで支える(ユーザー了承。低いピンヘッダーは JLC に無い)、DB9 は右の側面の VoiceS3R の後ろ、Grove は奥の面の DB9 の後ろ)。共通: 床 1.6・壁 1.8・天板 2.2(皿ねじの下に 1.25 残す)、基板は床のボス(高さ 2、M2 タッピング)、指静脈は A では床から立てた柱に載せ、B では本体と一体の台に載せてふたの段差受け(窓 57.5 × 25.5 + 裏の座ぐり 0.7、上面はふたから 0.5、指静脈 Unit P と同じ)で押さえる(VHB で貼るだけの固定はユーザーが却下)。B のふたは指静脈の上を覆い(窓と座ぐり)、VoiceS3R の角だけを窓の丸みの内側から切り欠く(細い部分を作らない)。指で押す力は、B では指静脈の台(棚と横木)が受ける(A は、ふたは DB9 の上と VoiceS3R のプラグの上を切り欠き、DB9 をふたから上に出して、中のケーブルの余りの上まで下げる。B は DB9 もふたの下。高さ A 16.5 / B 23.6(指静脈の台 3.9 + 段差受け))、ふたは平板 + 位置決めの縁(縁は壁の切り欠きと部品の近くでは幅ごと切る。細い残りは 1.0 mm の肉厚チェックで落ちる)で、M2 × 5 の皿タッピングねじで上から本体の壁の受け(3.9 × 6 × 高さ 4.5)に締める。受けの場所は `ledges()`(箱・ふた・リブ・干渉チェックの `shell_and_lid` / `rib_grid` / `check` と一緒に `station/shapes.py`、ふたの高さ `z_in` は引数)が部品・壁の穴・ふたの窓(皿穴から 1.0)を避けて四隅の近くから選び、3 本未満なら失敗(A は四隅に 4 本、B は奥の壁の 2 本と右の壁の DB9 の後ろの 1 本で 3 本(どれも基板の部品を xy で避け、基板は受けの所を切り欠いて上から入れる、`shapes.way_in`))。反り止めに、床(高さ 1.0、基板の下で THT の足とボスを避ける)とふたの裏(深さ 1.5、部品と窓を避ける)へ幅 1.2 のリブを約 12 おきの格子で入れる(JLC3DP に、ナイロンの平板・枠・中が空いた形は反りやすくリブが効くと言われた。2026-10-06)。リブは横切る物があると幅ごと切る(細い残りを作らない)。3D ページのひな形は部品のキー `shell`(上)と `lid`(下)を前提にしている(無いと 3D が出ない)。干渉があれば失敗、STL は CI の肉厚チェック(1.0)にかける。sw130j の形をそのまま造形した版は JLC3DP に発注済み(2026-10-05、4 台 $48.33、カバーの 0.8 未満の段をリブの面合わせで直して差し替え)。
- SW 案(`station/build_station_sw.py`、REV sw1、`site/station-sw/`): ケースを小さくするのが目的の別案。タカチ SW-85B(60 × 40 × 85、内寸 52.8 × 77.8 × 32.7)に ESP 基板 sw を ASL-12 で浮かせ、指静脈(M3 × 12、カバーから 3.8 出す)と NFC(M3 × 10、カバーの裏)を立てる。座標 = 基板座標(ケース中心、DB9 / USB-C の端が −y)。穴・ASL・部品の位置は `build_board.py` の `sw` と同じ値を持つので一緒に直す。
- 指静脈 Unit(`station/build_vein_unit.py cs|sic`、`site/vein-unit-cs/`・`site/vein-unit-sic/`、REV vu3〜): 指静脈モジュールだけを小さいタカチのケースに入れ、Grove 1 本(5V → LDO で 3.3V)で PortABC の PORT.C につなぐ案。机に並べて使う想定。`cs` = CS75N-B(35 × 75 × 12、ねじの柱の間にはめ込み、端のすき間で線を直付け)、`sic` = SIC5-9-2B(45 × 90 × 20、中いっぱいの基板を M2 ボス 4 本に留め、その上に指静脈、基板に Grove ソケット・LDO、付属ケーブル④(9P → 4P)の 9P 側の端子を 3〜6 に差し替え、指静脈の脇の真ん中の横向き J1(53261-0471)へまっすぐ挿す)。基板は `pcb/vein_unit_board/build_board.py`(u3、78 × 39、M2 × 4、配線もスクリプトに直書き、CI で gerber / CPL / DRC → `fab/vein_unit/`)。指静脈の位置(y −16.5〜9.5)と J1 の位置は 3D と基板の 2 か所にあるので一緒に直す。ケースはタカチ STP の実測値からの簡略形状(STP は入れない)。蓋の窓と端の穴の手加工用の原寸型紙 PDF(A4)もページから取れる。付属ケーブルは平らな窓の側の端面から水平に出る MX1.25 9P、反対側はデュポン。box ヘルパー・指静脈のイメージ形状・ページ出力は `station/shapes.py`(PF と共有)。原寸の型紙(外形 + 角丸長方形 / 円の穴のリスト、複数の面)は `station/template.py` の `cut_template`、寸法入り加工図(ezdxf の DXF + 同じ図の PDF)は `station/drawing.py` の `face` / `sheet` で、PF・指静脈 Unit・SW75 が共有する(どちらも CadQuery を使わない)。
- 指静脈 Unit P(`station/build_vein_unit_print.py`、REV vp3、`site/vein-unit-print/`): 指静脈モジュールだけを 3D 印刷(MJF PA12)の最小の箱に入れ、Grove 1 本で VoiceS3R の PORT.A に直接挿す案。箱は `shapes.shell_and_lid`(床 1.6・壁 1.8・ふた 2.2、M2 × 5 皿タッピングで壁の受けに留める、受け 3 本未満で失敗)。モジュールは実測の 2 段形(`shapes.vein_step_box`: 上から 2.0 が 57 × 25 の段、下が 59 × 26、底に 9P の端から 18〜28・深さ 2 の溝が横に貫通)で、段がふたの窓(57.5 × 25.5)を通り、胴がふたの裏の座ぐり(深さ 0.7、59.4 × 26.4)に当たって上面はふたから 0.5 出る。基板 u4(`pcb/vein_unit_board/build_board.py p`、77.1 × 30.0 の四隅をふたの受けの分(受け + 0.3、縁まで 2.0 未満なら縁まで)切り欠いた形、`NOTCHES` はケースと基板の 2 か所、`fab/vein_unit_p/`、BOM `jlc_bom_p.csv`、補正 `jlc_cpl_corrections_p.csv`)は床のリブの上でモジュールに押さえられ、横は壁で決まる(ねじ・ボスなし)。基板は部品ごと上から落とし込むので、ふたの受け(壁の内側 3.9、ふたから 4.5 下まで)を xy で避ける必要があり、スクリプトが受けの位置から切り欠きを確かめ、基板・J1・J2・LDO・指静脈・9P プラグが受けに当たらないことを assert する(ケーブルは手で通すので対象外)。部品は上面だけで、モジュールの下には置かない: J1 = 縦型 MX1.25 4P(53398-0471、C17617036)は −x 端の真ん中、9P プラグ(曲げた線とで端面から 2.0、実測、`CABLE_END`)のすぐ外側に立てて上から挿す(vp2。vp1 は +y の長い辺の横の帯にあり、幅が 4.6 太かった)。付属ケーブル④の余りは長い辺の両側面に厚さ 2.0(`CABLE_SIDE`、−y の実測)で折り返す前提で場所だけ取り、巻き方は実物で合わせる(底の溝も使える)。J1 の上はプラグ 5.7 + 線の曲がり `J1_ROOM` 1.8 で、ふたの受けの下に収める(4 隅に受け)。ピン順は 1 = 3V3 / 2 = GND / 3 = RXD / 4 = TXD(9P の 3〜6 の順、station 基板の J3 と違うのでシルクに明記)、U1 / C1 / C2 は +x 端の J2 の +y 側に縦一列(切り欠きの外)、Grove J2(JST S4B-PH-SM4-TB、C265102、CPL の回転補正 180 は station 基板の #96 と同じ)は +x の端面。外形・J1 / J2 の位置はケースと基板の 2 か所にあるので一緒に直す。u3(2026-09 発注分)は J2 が 180° 逆に付いている。標準の Grove ケーブルでは使わない。
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
