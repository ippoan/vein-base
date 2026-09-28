# vein-base

M5Stack **Atom VoiceS3R** の下に積むベースです。**指静脈モジュール Waveshare Finger Vein Scanner Module (A)** を UART でつなぐための中継基板と、上蓋なしの 1 部品のケース(カップ)で構成しています。

ケース(`vein_base_v<版>_cup`)は床・ネジのボス・基板を支えるレールに、基板を囲む壁を立ち上げた形です。M5 の Atomic 系ベースと同じく、VoiceS3R は Ext.Pin のピンに刺して上に載せるだけで、外側は囲みません。壁の上端は VoiceS3R の底面から 0.25 mm 下で止め、ピンヘッダーのすき間を隠します(外形 24.4 × 33.1 × 9.25 mm、壁は全方向 1.4 mm 以上)。基板に合わせて USB-C と反対側(+y)へ伸びていて、その面に J3 のケーブル用の上へ開いた溝があります。

**3D プレビュー:** https://ippoan.github.io/vein-base/(回転・分解表示・部品の表示切替ができます)

3D プレビュー(GitHub Pages、main の CI が更新。各ページから型紙・加工図もダウンロードできます):

| 案 | ページ |
|---|---|
| vein-base(単体) | https://ippoan.github.io/vein-base/ |
| Vein Station(印刷筐体) | https://ippoan.github.io/vein-base/station/ |
| Vein Station SE(CoreS3 SE) | https://ippoan.github.io/vein-base/station-se/ |
| Vein Station PF(タカチ PF13-4-9) | https://ippoan.github.io/vein-base/station-pf/ |
| Vein Station SW(タカチ SW-85B) | https://ippoan.github.io/vein-base/station-sw/ |
| Vein Station SW75(タカチ SW-75B) | https://ippoan.github.io/vein-base/station-sw75/ |
| Vein Station SW130(タカチ SW-130B) | https://ippoan.github.io/vein-base/station-sw130/ |
| 指静脈 Unit(CS75N-B) | https://ippoan.github.io/vein-base/vein-unit-cs/ |
| 指静脈 Unit(SIC5-9-2B) | https://ippoan.github.io/vein-base/vein-unit-sic/ |

## 構成

```
VoiceS3R(Ext.Pin メス)
  └ 中継基板 20.0×29.9 mm(J1 1x5 / J2 1x4 オスピン、J3 MX1.25 4P 横型。全部品が表面 = VoiceS3R 側。J3 は VoiceS3R の外、USB-C の反対側の端)
  └ カップ 24.4×33.1(基板の下と周りだけ。VoiceS3R は囲まない。M2×12 ネジ 1 本で全体を VoiceS3R に共締め)
```

組み立て: VoiceS3R に基板を挿す → 指静脈のケーブルを J3 に挿す(挿さり具合を目で確かめられる)→ カップを下から差し込む(ケーブルは USB-C と反対側(+y)の壁の、上へ開いた溝を通る)→ 底から M2 ネジで締める。

- **挿し口:** 指静脈ケーブル(J3)は、VoiceS3R の USB-C / PORT.A(NFC 用)と**反対の面**に出ます。J3 は高さ 3.4 mm で VoiceS3R の下(すき間 2.54 mm)に入らないため、基板を VoiceS3R の外まで伸ばして載せています。
- **ケーブル:** 指静脈モジュール付属の 9P→4P ケーブルを使います。9P 側の端子を 1→5、2→6 の位置へ差し替えてください。
  付属ケーブルが使えない(端子の差し替えができない・長さが合わない)場合は、最悪 [eleshop.jp のハーネス製作](https://eleshop.jp/shop/e/eHARNESS/) で 4P(MX1.25)↔ 9P のケーブルを見積もります。

## 配線

| VoiceS3R Ext.Pin | 基板 | J3(4P) | モジュール 9P |
|---|---|---|---|
| G5(UART TX) | J1-2 | 1 | 5 RXD |
| G6(UART RX) | J1-3 | 2 | 6 TXD |
| 3V3 | J1-1 | 3 | 3 VCC |
| GND | J2-4 | 4 | 4 GND |

- UART は 57600 bps。
- NFC(M5Stack Unit NFC U216)は本体の PORT.A を使用(I2C:SDA=G2、SCL=G1)。

## ATOMIC Proto Kit 版(`vein_base_atomic`)

3D プリントのカップの代わりに、市販の M5Stack ATOMIC Proto Kit(A077)のケースに入れる版。基板の外形は M5 公式の ATOMIC-TYPE-A([M5_Hardware](https://github.com/m5stack/M5_Hardware) の `Common/Atomic_Type_A/Structures/Atomic_Type_A.dxf`、20 × 43.8 mm)をそのまま使い、中心の穴は φ4.2(メッキなし)。部品・配線表はカップ版と同じで、J3 は +y 端(ケース端面の開口側)に置く。両側の半円の切り欠き(ケースの柱よけ)のあいだは幅 8.6 mm しかないので、配線はそこを x −3.8〜+3.8 の中だけで通る。

- **発注対象は `fab/atomic/vein_base_atomic_v<版>_*`**(ガーバー zip・BOM・CPL)。カップ版の `vein_base_v<版>_*` と取り違えない。
- **JLCPCB では板厚 1.0 mm を選ぶ**(カップ版は 1.6 mm)。
- 手で確かめる項目: J3 に挿したプラグがケース端面の開口 16 × 9.3 mm を通るか、ケースの柱 φ4.84 が基板の切り欠きに入るか。

## Vein Station(一体筐体・案)

VoiceS3R(vein-base の基板のみ。ケースは使わない)・指静脈モジュール・NFC ユニットを上向きに並べて収める卓上筐体の案。`station/build_station.py`(CadQuery)が筐体(ケース上部・底蓋)の STEP / STL と 3D プレビュー(https://ippoan.github.io/vein-base/station/)を作り、モジュール・プラグ・USB ケーブルとの干渉をチェックする。モジュールの外形は公式値(VoiceS3R・NFC は M5Stack 公式 STL の [Atom_VoiceS3R.stl](https://github.com/m5stack/M5_Hardware/blob/a240115c94b19ecf647f229c47fa9a8ce46ccdc4/Products/C126-ECHO_Atom_VoiceS3R/Structures/Atom_VoiceS3R.stl)・[Unit_NFC.stl](https://github.com/m5stack/M5_Hardware/blob/a240115c94b19ecf647f229c47fa9a8ce46ccdc4/Products/U216_Unit_NFC/Structures/Unit_NFC.stl)、指静脈は [Waveshare の製品ページ](https://www.waveshare.com/finger-vein-scanner-module-a.htm) の 59 × 26 × 15)。上面ボタン・ネジ頭などの細部とケーブルは写真からの実測。指静脈のコネクタ位置は未確定。基板は `pcb/station_board/`(r12)が生成する 60 × 35 mm の 1 枚基板で、VoiceS3R の Ext.Pin・指静脈 J3(G5/G6)・MAX3232(G7=送信 / G8=受信)・DIP(1+2 = Passthrough、3+4 = Cross)・DB9 オス RA をまとめ、接続口はすべて奥の壁に出す。同じ回路・同じ配線で外形を広げた版(`build_board.py pf` → `station_board_pf`、92 × 71)は、既製ケースタカチ PF13-4-9 用(印刷部品なし)。基板はケースに元からある基板用ボス(87 × 47)にタカチ TPS-M2.3-7 と M2.3 ねじで留め、モジュールは M3 オスメス六角スペーサーとナットで基板に立てる。60 × 35 の範囲と配線は共通。ケース側は `station/build_station_pf.py`(ケースはタカチ公式 STP の実測値からの簡略形状、STP は入れない)が、干渉チェック・3D プレビュー(`site/station-pf/`)・タカチの穴加工に出す DXF(天板の窓 2 つだけ)を作る。接続口はすべて背面なので背面パネルは付けない。基板の穴(H1..H8、B1..B4)はこのスクリプトと `build_board.py` の 2 か所にあるので一緒に直す。

### Vein Station ESP 基板(VoiceS3R の回路を基板に載せた版・案)

`pcb/station_esp_board/build_board.py`(e1)は、PF13-4-9 用の station 基板(92 × 71、穴・DB9・MAX3232・DIP・J3 の位置は同じ)に、Atom VoiceS3R を挿す代わりにその回路を直接載せた版。M5Stack 公開の回路図(`Sch_M5_AtomS3R_v0.4.1` / `Sch_M5_AtomEchoS3R_Audio_v1.0`)と同じ GPIO でつなぐので、VoiceS3R 用のファームがそのまま使える見込み。

- ESP32-S3-WROOM-1-N8R8(技適付きモジュール。VoiceS3R の PICO-1 と同じ Flash 8 MB / PSRAM 8 MB)。アンテナは背面(−y)の端から 1.25 mm はみ出す。
- USB-C(G19 / G20 を直結)、AMS1117-3.3、EN / BOOT ボタン。
- ES8311(I2C: SDA G45 / SCL G0、I2S: MCLK G11 / BCLK G17 / WS G3 / G48 → DSDIN / ASDOUT → G4)、MEMS マイク(LinkMems LMA3729T381。VoiceS3R のマイクは在庫切れ)、NS4150B(CTRL G18)、13 × 13 mm の SMD スピーカー。スピーカーとマイクは、PF の天板にある旧 VoiceS3R 用の窓の下に置く。
- Grove 2 口: J6 = Unit NFC(G2 SDA / G1 SCL、VoiceS3R の PORT.A と同じ)、J7 = 予備(G38 / G39)。IR LED は載せない(G47 は空き)。
- **初回だけ**: G45(SDA のプルアップ付き)は Flash 電圧のストラップなので、最初に BOOT を押したまま EN を押し、`espefuse.py --port <ポート> set_flash_voltage 3.3V` で Flash 電圧を eFuse に書く。M5Unified は PICO-1 のパッケージで VoiceS3R を見分けるので、`cfg.fallback_board = m5::board_t::board_M5AtomVoiceS3R` を指定する。
- 外形は 2 種類(回路は同じ): PF13-4-9 用 92 × 71(`build_board.py`、`fab/station_esp/`。筐体側 `station/build_station_pf.py` はまだ VoiceS3R 版のまま)と、SW-85B 用 52 × 76(`build_board.py sw`、`fab/station_esp_sw/`)。
- 配線は freerouting 2.4.1 の結果を `station_esp_board[_sw].ses` に入れてある(`build_board.py [sw] dsn` で DSN を出して再配線)。CI で gerber / CPL / DRC。

### Vein Station SW(タカチ SW-85B・別案)

ケースを小さくする案。VoiceS3R が無くなった分、中身は指静脈・NFC・DB9 と ESP 基板だけなので、タカチで一番小さく収まる SW-85B(60 × 40 × 85、はめ込み式、¥350。PF13-4-9 の半分以下の面積)に入れる。`station/build_station_sw.py` がケースの簡略形状(タカチの外形図から)と干渉チェック、3D プレビュー(`site/station-sw/`)を作る。

- 基板(52 × 76)は床に貼るタカチ ASL-12 × 3 に差し込む(床のリブの間)。指静脈は M3 × 12 の上に立てて、カバーの窓から 3.8 出す。NFC は M3 × 10 の上で、カバーの裏に貼る(窓なし)。
- 加工はカバーの窓(指静脈)とスピーカー・マイクの穴、端面の DB9 のフードが入る角穴・USB-C プラグの穴・J7 ケーブルの穴。
- 幅の余裕は小さい(指静脈 26 + NFC 24 に対して内寸 52.8)。発注前に指静脈の実物を測る。床のリブの高さは図面に無いので 2.0 と仮定。

### Vein Station SW75(タカチ SW-75B・NFC を外に出す最小案)

NFC Unit を箱の外に置き(Grove ケーブルで J6 へ)、SW-75B(50 × 30 × 75、¥200。PF13-4-9 の約 1/3 の面積で高さも 10 低い)に指静脈・DB9 と ESP 基板だけを収める。`station/build_station_sw75.py` が干渉チェックと 3D プレビュー(`site/station-sw75/`)、基板は `build_board.py sw75`(40.8 × 68.1、`fab/station_esp_sw75/`、BOM は `jlc_bom_sw75.csv`)。

- 片面実装のまま収めるため、抵抗・コンデンサは 0402、LDO は SOT-89、ボタンは Alps SKRPACE010(4.2 × 3.2)、線幅 / 間隔は 5 / 5 mil。
- DIP スイッチの代わりに 0 Ω(R11 / R12 = ストレート、実装済み)とはんだジャンパー(JP1 / JP2 = クロス)。クロスにするときは R11 / R12 を外して JP1 / JP2 をはんだでつなぐ。
- DB9 と USB-C は +x の側面、Grove 2 口は +y の端面から出す。WROOM のアンテナは -x の壁側。
- 基板は指静脈の M3 × 6 スペーサーにぶら下げる形で、うち 2 本(H1 / H4)のオス側を床に貼るタカチ ASR-7 にねじ込む。指静脈はカバーから 2.8 出す。
- 指静脈のケーブル: モジュールの -y 端のソケットから出て、基板の -y 端の切り欠き(6 × 2.5)から基板の下へ逃がし、余りは基板の下(床まで 7.2)に収める。同じ切り欠きから J3(口は同じ -y 向き)へ入る。

### Vein Station SW130(タカチ SW-130B・全部入りの細い案)

タカチ SW-130B(40 × 25 × 130、¥360)に、−y から DB9 → DIP と指静脈のケーブル → 指静脈 → VoiceS3R を一列に全部入れる。`station/build_station_sw130.py` が干渉チェック・3D プレビュー(https://ippoan.github.io/vein-base/station-sw130/)・加工図(DXF / PDF)と A4 原寸の型紙、基板は `build_board.py sw130`(34.8 × 122.7、片面、`fab/station_sw130/`、BOM は `jlc_bom_sw130.csv`)。詳細は `CLAUDE.md` の SW130 案の節。

### Vein Station SE(CoreS3 SE 版・案)

本体を CoreS3 SE に替え、RS232M Module 13.2(アルコールチェッカー FC-1200 用)・NFC・指静脈を収める版。LAN は使わず、USB 1 本で Windows PC につなぐ。`station/build_station_se.py` が筐体と 3D プレビュー(https://ippoan.github.io/vein-base/station-se/)を作る。CoreS3 SE には PORT.B のコネクタが無いので、指静脈の UART(G8/G9)は RS232M の下に挿す M-Bus 分岐基板から取り出す。CoreS3 SE と Unit NFC は M5Stack 公式 STL([m5stack/M5_Hardware](https://github.com/m5stack/M5_Hardware)、MIT)を commit 固定で取得して表示とポート位置に使う(`station/cad/`、git 管理外)。CoreS3 SE の PWR・USB-C・PORT.A はすべて左側面にある。指静脈モジュールの外形は公式値(コネクタ位置は未確定)。RS232M・分岐基板は仮の箱。計画は #14。

## フォルダ構成

| パス | 内容 |
|---|---|
| `pcb/` | KiCad 7 の基板データと生成スクリプト(`build_pcb.py`、KiCad 付属の Python で実行) |
| `VERSION` | 版番号。出力ファイル名(`vein_base_v<版>_*`)と基板裏のシルクに入る |
| `case/` | ケース生成スクリプト(`build_case.py`、CadQuery) |
| `pcb/jlc_bom.csv` | JLCPCB 用 BOM の元データ(LCSC 品番) |
| `pcb/station_board/jlc_bom.csv` | station 基板の JLCPCB 用 BOM の元データ |
| `pcb/station_esp_board/jlc_bom.csv` | station ESP 基板(VoiceS3R の回路を載せた版、PF 用・SW 用で共通)の JLCPCB 用 BOM の元データ |
| `pcb/station_esp_board/jlc_bom_sw75.csv` | 同じく SW-75B 用(0402 部品)の BOM |
| `fab/` | CI の出力先(git 管理外)。JLCPCB 発注用(ガーバー zip、BOM、CPL)、原寸の確認用 PDF、基板の STEP |
| `tools/` | CI 用スクリプト(DRC チェック、JLC 用 CPL 変換、3D プレビュー生成と干渉チェック) |

## CI(GitHub Actions)

`main` への push で `.github/workflows/build.yml` が次を順に実行します。

1. KiCad 7 で基板を生成する。ガーバー、ドリル、CPL、原寸 PDF、STEP を出力する。
2. DRC をかけ、違反があれば失敗させる。
3. CadQuery でケースを生成する。
4. 3D プレビューを生成し、ケースと部品・VoiceS3R の干渉チェックを行う(干渉があれば失敗)。
5. 製造データを Artifacts(`vein-base-v<版>-fab`)にアップロードする。ファイル名はすべて `vein_base_v<版>_*` で、発注時に版を取り違えないようにしている。STL / STEP / PDF 等の生成物はリポジトリに置かず、常に Artifacts から取る。
6. 3D プレビューを GitHub Pages に公開する。

寸法や配線を変えるときは、`pcb/build_pcb.py` / `case/build_case.py` を編集して push すれば、製造データと 3D プレビューがまとめて更新されます。

## 設計根拠と検証

- **ピンヘッダー位置とネジ穴:** M5Stack 公式 [M5_Hardware](https://github.com/m5stack/M5_Hardware) の `Common/Atomic_Type_A` による。
- **ピン割り当て:** VoiceS3R 本体底面のシルク印刷による。
- **KiCad DRC:** 未接続 0、クリアランス違反なし。
- **干渉チェック:** 基板、部品、ケーブル、ネジ、VoiceS3R の外形との干渉は体積 0(問題なし)。

## 発注前の確認(未検証の項目)

1. `vein_base_v<版>_fitcheck_1to1_seen_from_below.pdf` を原寸(100%)で印刷し、VoiceS3R の底面に当てる。ピン列の左右とネジ穴の位置が合うか確認する。
2. 付属ケーブルの結線がストレート(4P の n 番 = 9P の n 番)か、テスターで確認する。
3. 実装は JLCPCB の Economic PCBA(片面、Top)で全部品を付ける。J3 は LCSC C696092(Molex 53261-0471)。JLC の実装プレビューで、J1/J2/J3 がすべて表面に載り、J3 の開口が基板の +y 端(USB-C と反対)を向いているか確認する。
4. M2 ネジの長さ、VoiceS3R のメスヘッダーの深さ、VoiceS3R 底面の出っ張りの有無を実物で確認する。
5. ケースの素材は DMM.make の「PA12｜MJF」(グレー、磨きなし)。形の確認だけならエコノミーレジン(SLA)でよい。
