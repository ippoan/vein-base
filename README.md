# vein-base

M5Stack **Atom VoiceS3R** の下に積むベースです。**指静脈モジュール Waveshare Finger Vein Scanner Module (A)** を UART でつなぐための中継基板と、上蓋なしの 1 部品のケース(カップ)で構成しています。

ケース(`vein_base_v<版>_cup`)は床・ネジのボス・基板を支えるレールに壁を立ち上げ、VoiceS3R の下端 3 mm にかぶせる形です(すき間 0.25 mm、外形 27.3 mm 角、壁は全方向 1.4 mm 以上)。PORT.A のある面はかぶせる部分を切り欠き、J3 のケーブル用に上へ開いた溝があります。

**3D プレビュー:** https://ippoan.github.io/vein-base/(回転・分解表示・部品の表示切替ができます)

## 構成

```
VoiceS3R(Ext.Pin メス)
  └ 中継基板 20.0×29.9 mm(J1 1x5 / J2 1x4 オスピン、J3 MX1.25 4P 横型。全部品が表面 = VoiceS3R 側。J3 は VoiceS3R の外、USB-C の反対側の端)
  └ カップ 27.3×27.3(VoiceS3R の下端にかぶせる。M2×12 ネジ 1 本で全体を VoiceS3R に共締め)
```

組み立て: VoiceS3R に基板を挿す → 指静脈のケーブルを J3 に挿す(挿さり具合を目で確かめられる)→ カップを下から差し込む(ケーブルは溝を通る)→ 底から M2 ネジで締める。

- **挿し口:** 指静脈ケーブル(J3)は、VoiceS3R の USB-C / PORT.A(NFC 用)と**反対の面**に出ます。J3 は高さ 3.4 mm で VoiceS3R の下(すき間 2.54 mm)に入らないため、基板を VoiceS3R の外まで伸ばして載せています。
- **ケーブル:** 指静脈モジュール付属の 9P→4P ケーブルを使います。9P 側の端子を 1→5、2→6 の位置へ差し替えてください。

## 配線

| VoiceS3R Ext.Pin | 基板 | J3(4P) | モジュール 9P |
|---|---|---|---|
| G5(UART TX) | J1-2 | 1 | 5 RXD |
| G6(UART RX) | J1-3 | 2 | 6 TXD |
| 3V3 | J1-1 | 3 | 3 VCC |
| GND | J2-4 | 4 | 4 GND |

- UART は 57600 bps。
- NFC(M5Stack Unit NFC U216)は本体の PORT.A を使用(I2C:SDA=G2、SCL=G1)。

## Vein Station(一体筐体・案)

VoiceS3R(vein-base の基板のみ。ケースは使わない)・指静脈モジュール・NFC ユニットを上向きに並べて収める卓上筐体の案。`station/build_station.py`(CadQuery)が筐体(ケース上部・底蓋)の STEP / STL と 3D プレビュー(https://ippoan.github.io/vein-base/station/)を作り、モジュール・プラグ・USB ケーブルとの干渉をチェックする。指静脈モジュールは採寸待ちのため仮の箱。基板は `pcb/station_board/`(r10)が生成する 60 × 35 mm の 1 枚基板で、VoiceS3R の Ext.Pin・指静脈 J3(G5/G6)・MAX3232(G7=送信 / G8=受信)・DIP(1+2 = Passthrough、3+4 = Cross)・DB9 オス RA をまとめ、接続口はすべて奥の壁に出す。

### Vein Station SE(CoreS3 SE 版・案)

本体を CoreS3 SE に替え、RS232M Module 13.2(アルコールチェッカー FC-1200 用)・NFC・指静脈を収める版。LAN は使わず、USB 1 本で Windows PC につなぐ。`station/build_station_se.py` が筐体と 3D プレビュー(https://ippoan.github.io/vein-base/station-se/)を作る。CoreS3 SE には PORT.B のコネクタが無いので、指静脈の UART(G8/G9)は RS232M の下に挿す M-Bus 分岐基板から取り出す。CoreS3 SE と Unit NFC は M5Stack 公式 STL([m5stack/M5_Hardware](https://github.com/m5stack/M5_Hardware)、MIT)を commit 固定で取得して表示とポート位置に使う(`station/cad/`、git 管理外)。CoreS3 SE の PWR・USB-C・PORT.A はすべて左側面にある。RS232M・指静脈モジュール・分岐基板は仮の箱。計画は #14。

## フォルダ構成

| パス | 内容 |
|---|---|
| `pcb/` | KiCad 7 の基板データと生成スクリプト(`build_pcb.py`、KiCad 付属の Python で実行) |
| `VERSION` | 版番号。出力ファイル名(`vein_base_v<版>_*`)と基板裏のシルクに入る |
| `case/` | ケース生成スクリプト(`build_case.py`、CadQuery) |
| `pcb/jlc_bom.csv` | JLCPCB 用 BOM の元データ(LCSC 品番) |
| `pcb/station_board/jlc_bom.csv` | station 基板の JLCPCB 用 BOM の元データ |
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
