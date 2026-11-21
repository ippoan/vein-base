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
| Vein Station 3D 印刷の試作 A(一列・薄型) | https://ippoan.github.io/vein-base/station-print-a/ |
| Vein Station 3D 印刷の試作 B(2 列・短い) | https://ippoan.github.io/vein-base/station-print-b/ |
| Vein Station 3D 印刷の案 C(一列・DB9 なし・指静脈と VoiceS3R だけ) | https://ippoan.github.io/vein-base/station-print-c/ |
| 指静脈 Unit(CS75N-B) | https://ippoan.github.io/vein-base/vein-unit-cs/ |
| 指静脈 Unit(SIC5-9-2B) | https://ippoan.github.io/vein-base/vein-unit-sic/ |
| FP008 の USB 基板(FP008 の裏のふた f6、RP2354A 入り) | https://ippoan.github.io/vein-base/fp008-board/ |

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
- **J1 / J2 は差し込み側 4 mm の XFCN PZ254V-11-05P-A40(C42419912)/ -04P-A40(C42419911)**(v0.16〜)。v0.14 の ZHOURI(差し込み側 6 mm)は VoiceS3R が 1〜2 mm 浮いたため。
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

タカチ SW-130B(40 × 25 × 130、¥360)に、−y から DB9 → DIP と指静脈のケーブル → 指静脈 → VoiceS3R を一列に全部入れる。`station/build_station_sw130.py` が干渉チェック・3D プレビュー(https://ippoan.github.io/vein-base/station-sw130/)・加工図(DXF / PDF)と A4 原寸の型紙、タカチへの見積もり依頼に付ける加工位置図(A4 横 1 枚・日本語、`vein_station_<REV>_positions.pdf`)を作る。基板は `build_board.py sw130`(34.8 × 122.7、片面、`fab/station_sw130/`、BOM は `jlc_bom_sw130.csv`)。詳細は `CLAUDE.md` の SW130 案の節。

### Vein Station SE(CoreS3 SE 版・案)

本体を CoreS3 SE に替え、RS232M Module 13.2(アルコールチェッカー FC-1200 用)・NFC・指静脈を収める版。LAN は使わず、USB 1 本で Windows PC につなぐ。`station/build_station_se.py` が筐体と 3D プレビュー(https://ippoan.github.io/vein-base/station-se/)を作る。CoreS3 SE には PORT.B のコネクタが無いので、指静脈の UART(G8/G9)は RS232M の下に挿す M-Bus 分岐基板から取り出す。CoreS3 SE と Unit NFC は M5Stack 公式 STL([m5stack/M5_Hardware](https://github.com/m5stack/M5_Hardware)、MIT)を commit 固定で取得して表示とポート位置に使う(`station/cad/`、git 管理外)。CoreS3 SE の PWR・USB-C・PORT.A はすべて左側面にある。指静脈モジュールの外形は公式値(コネクタ位置は未確定)。RS232M・分岐基板は仮の箱。計画は #14。

## FP008 の USB 基板(`pcb/fp008_board`、f6)

Grow の顔・手のひら静脈認証モジュール FP008(楕円 59.5 × 38.5、UART と USB の両方が出る、赤外線の近接センサー付き、命令は FP001S と同じ)を、**USB-C 1 本**で PC につなぐ基板。**f3 から基板が FP008 の裏のふた**になる(後ろの本体 55.45 × 34.45 の角丸の形、FP008 の後ろの 4 つのねじ穴(中心から ±18.35, ±11.95、マニュアルの図からの読み取り)に M2 で留める。2026-11-19 ユーザー指定)。**f4 から部品は内側**(FP008 の中を向く。片面のままなので JLC の Economic で付く)で、外に出るのはケーブルだけ。**f5 から舌は無く、基板は本体の形からはみ出さない**(2026-11-20 ユーザー指定)。USB-C は左右の端の近くに 1 つずつ(口は外向き)で、その先の基板に窓(8.8 × 13.4)を開け、ケーブル側の L 字の変換(オス → 90° のメス)の胴が窓を通って後ろへ出る。変換は基板を FP008 から外して挿す。変換の根元は FP008 の後ろのくぼみに入る(基板から約 5.1 下まで。変換の寸法 12.4 × 7.5 は製品写真からの見積もりで、くぼみの深さと一緒に実物で確かめる)。部品はねじのボスから 3.5 離す。**f6 から RP2354A を載せる**(2026-11-21 ユーザー決定。f1〜f5 はマイコン無しの CH340C で、鍵は PC の TPM だった(2026-11-19))。RP2354A が FP008 の UART を持ち、鍵・顔認証のシリアルの手続き・署名つきのシリアル OTA(A / B と戻し)をマイコン側でやる。ファームは alc-app-s3 の `crates/fp001s-rp2354`(FP008 は命令が FP001S と同じ EF AA。IRQ の GPIO と DEVICE の種別はファーム側で足す)。形(外形・ねじ穴・窓・J1 / J2 / J3 の位置・部品の高さ 3.3 まで)は f5 のまま。音は PC のスピーカーから出す。PC からは FP008 のカメラ(UVC)と RP2354A(USB CDC)の 2 つが見える。

- J1(USB-C): PC へ。VBUS → 5 V(FP008 の本体はこの 5 V で動く。降圧は無い)、CC は 5.1 kΩ × 2。D+ / D- は USBLC6 → CH334F ハブ。ポートは WCH のデータシート V2.4 の表 1-3(4F の列)で、1(11 / 12)= FP008 の USB、2(9 / 10)= RP2354A、3(7 / 8)= J2、4 は空き。
- 3D: https://ippoan.github.io/vein-base/fp008-board/ (main の CI が更新。部品は CI が取ってくる KiCad の 3D モデル、USB-C はモデルが無いので箱。RP2354A とそのまわりは Raspberry Pi の参考設計のフットプリントで 3D モデルが無く、出ない)。部品込みの STEP は Artifacts の `fab/fp008/fp008_board_v<版>_full.step`。
- J2(USB-C、+x の端、J1 の反対側): USB スピーカーなどの機器を挿す口(ハブのポート 3)。VBUS は 5 V に直結(スイッチ・ヒューズ無し)、CC は 56 kΩ × 2 で 5 V へ(既定の USB 電力を知らせる Rp)、D+ / D- は USBLC6。電源は全部 PC のポートから来るので、USB 2.0 の 500 mA のポートなら J2 の機器は 250 mA 程度まで。
- U6(RP2354A、QFN-60、フラッシュ 2 MB 内蔵、無線なし): ハブのポート 2 に USB(R107 / R108 27 Ω)。UART0 は **GP0 TX → FP008 の RX(J3 4 番)、GP1 RX ← FP008 の TX(J3 3 番)**(115200 8N1)、**FP008 の IRQ(J3 5 番、人が来ると High)は GP2**(GP0 / GP1 の隣のピン 4。f5 では CH340C の CTS#)。IRQ には抵抗を入れていない(FP008 が押し引きで出す前提。内部プルダウンは RP2350 の E9 の不具合があるので、ファームで使わない)。
- RP2354A まわり(レギュレーター L106 / C106 / C107 / C109 / R103、水晶 Y106 と C103 / C104 / R102、100 nF の C108・C110〜C118)は Raspberry Pi の「RP2350A Minimal」(MIT)の配置・銅(フットプリント・線・ビア・ゾーン)をそのまま写す。データは `pcb/fp008_board/` の `rp2350_core.json`(同じ場所の `rp_core_extract.py` で作る。ライセンス表示 `rp2350_core_LICENSE.txt`)で、基板への取り込みは `pcb/fp008_board/rp_core.py`(どの基板からも import できる形)。0.25 の穴は 0.3 に広げ、RP2354A の上の 3V3 の面はパッドをベタでつなぐ(サーマルだと U6 の 1 番が DRC の starved_thermal で落ちた)。線幅 / クリアランスは 0.2 / 0.12(コアが 0.127)、3V3 は 0.3、5V は 0.5。
- BOOTSEL(TP1 = QSPI_SS を R110 1 kΩ 経由、TP2 GND とショートして電源投入で ROM の USB 書き込み)、RUN(TP3、R111 10 kΩ プルアップ)、SWD(TP4 SWDIO / TP5 SWCLK)はテストパッドで、**基板の裏(B、FP008 の外側)の左下**に並べる(基板を FP008 に留めたまま外から当てられる。ねじの頭・窓からは離してある)。新品の RP2354A はフラッシュが空なので、電源投入だけで ROM の USB 書き込みに入る(FP001S の基板の節と同じ)。
- U1(XC6206、LDO、200 mA)は f5 のまま。5 V から RP2354A と FP008 のセンサーの電源(6 番、60 µA)の 3.3 V を作る。**降圧にしない理由**: 3.3 V に載るのは RP2354A の多くて約 50 mA(150 MHz で USB ありが約 30 mA、内蔵フラッシュの書き込みが約 15 mA)とセンサーだけで、XC6206 の 200 mA の 1/4、損失は (5 − 3.3) × 0.05 ≒ 0.09 W で SOT-23 に収まり、VBUS が 4.4 V に下がっても落ちない(50 mA での落差は約 0.1 V)。モジュール FP001S は自身の 400 mA が 3.3 V に載るので降圧が要るが、FP008 の本体は 5 V で動く。5 V の合計は FP008 200 mA + ハブ約 30 mA + RP2354A 約 50 mA(+ J2 の機器)。
- J3(Molex PicoBlade 53261-0871、MX1.25 8P): FP008 のケーブル。1 = 5V、2 = GND、3 = TX(モジュールの出力)、4 = RX、5 = IRQ、6 = センサーの 3V3、7 = D+、8 = D-(マニュアル 1.3.2 の並び)。**発注前にケーブルが 1 番 → 1 番か実物で確認する**。
- 発注前に実物で確かめる: ねじ穴の位置と太さ、本体の角の形、**FP008 の後ろのくぼみに部品(高さ 3.3 まで)が入るか**、中のソケットの位置、ケーブルの長さ。
- 発注の設定: **JLC の Economic PCBA は表面処理 OSP では選べない**(HASL か ENIG にする)。
- 配線は freerouting 2.4.1 の `fp008_board.ses`(f6 で引き直し)。CI で `fab/fp008/` にガーバー・CPL・BOM・DRC・STEP。CPL 補正のうち、SOT-23(180)・PicoBlade 8P(4P と同じ 0 / −0.95)は類推で、発注時の実装プレビューで確かめる。RP2354A(C41378174)・L106・Y106 は EasyEDA の部品データと突き合わせて補正なし(0°)。f5 の SOIC-16(CH340C)の補正は消した。部品の種類: Extended は USB-C・USBLC6・CH334F・PicoBlade 8P・RP2354A・L106(AOTA)・Y106(ABM8)・27 Ω 0402 の 8 種(BOM の注記で Basic と書いていないもの。f5 から CH340C が抜けて RP2354A・L106・Y106・27 Ω が入り、+3)、ほかは Basic。

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
| `pcb/fp008_board/jlc_bom.csv` | FP008 の USB 基板の JLCPCB 用 BOM の元データ |
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
- **station 基板の RS232(実機テスト済み、2026-10-01):** 届いた station 基板 r10 に VoiceS3R を挿し、[alc-app-s3](https://github.com/ippoan/alc-app-s3) の `atoms3-timecard` の `station` 版(`0.1.0+74579fe`、Pages の `firmware/alc-hub-atoms3-timecard-station-merged.bin` を `espflash write-bin 0x0` で書き込み)で確認。SW1 は 1+2 ON(Passthrough)。DB9 に FC-1200B をつなぎ、G7 = 送信 / G8 = 受信(MAX3232、9600 8N1)で接続応答 → 暖機 → 吹き込み待ち → 測定 → 測定値(0.000 mg/L)まで USB コンソールに出た。未確認: 指静脈(J3、G5/G6。`vein` 版のファームが要る)、NFC、SW1 の Cross(3+4 ON)。

## 発注前の確認(未検証の項目)

1. `vein_base_v<版>_fitcheck_1to1_seen_from_below.pdf` を原寸(100%)で印刷し、VoiceS3R の底面に当てる。ピン列の左右とネジ穴の位置が合うか確認する。
2. 付属ケーブルの結線がストレート(4P の n 番 = 9P の n 番)か、テスターで確認する。
3. 実装は JLCPCB の Economic PCBA(片面、Top)で全部品を付ける。J3 は LCSC C696092(Molex 53261-0471)。JLC の実装プレビューで、J1/J2/J3 がすべて表面に載り、J3 の開口が基板の +y 端(USB-C と反対)を向いているか確認する。
4. M2 ネジの長さ、VoiceS3R のメスヘッダーの深さ、VoiceS3R 底面の出っ張りの有無を実物で確認する。
5. ケースの素材は DMM.make の「PA12｜MJF」(グレー、磨きなし)。形の確認だけならエコノミーレジン(SLA)でよい。
