# Extract-RFA-file

Extracts and decodes metadata from Revit `.rfa` files, including the `BasicFileInfo.bin` content.
Thanks to: [PeterHirn - phi-ag/rvt-app](https://github.com/phi-ag/rvt-app?tab=readme-ov-file)

Sample output:

```
File: racbasicsamplefamily\BasicFileInfo.bin
Size: 2305 bytes

=== UTF-16 BE decoded (ASCII-ish) ===
$ 00000000-0000-0000-0000-000000000000 ENU Autodesk Revit
 orksharing: Not enabled
Username:
Central Model Path:
Format: 2020
Build: 20190207_1515(x64)
Last Save Path: C:\Users\hansonje\OneDrive - autodesk\FY-2020 Projects\Revit - 142304 Update Files for 2020\2019 Files\rac_basic_sample_family.rfa
Open Workset Default: 3
Project Spark File: 0
Central Model Identity: 00000000-0000-0000-0000-000000000000
Locale when saved: ENU
All Local Changes Saved To Central: 0
Central model's version number corresponding to the last reload latest: 64
Central model's episode GUID corresponding to the last reload latest: c749ca88-5442-46eb-a706-04db158b688e
Unique Document GUID: c749ca88-5442-46eb-a706-04db158b688e
Unique Document Increments: 64
Model Identity: 00000000-0000-0000-0000-000000000000
IsSingleUserCloudModel: F
Author: Autodesk Revit

=== UTF-16 LE decoded (ASCII-ish) ===
2020 20190207_1515(x64) C:\Users\hansonje\OneDrive - autodesk\FY-2020 Projects\Revit - 142304 Update Files for 2020\2019 Files\rac_basic_sample_family.rfa @ $ c749ca88-5442-46eb-a706-04db158b688e$ c749ca88-5442-46eb-a706-04db158b688e 64$ 00000000-0000-0000-0000-000000000000

=== Parsed Key/Value fields ===
  all_local_changes_saved_to_central: 0
  author: Autodesk Revit
  build: 20190207_1515(x64)
  central_model_identity: 00000000-0000-0000-0000-000000000000
  central_model_path:
  central_model_s_episode_guid_corresponding_to_the_last_reload_latest: c749ca88-5442-46eb-a706-04db158b688e
  central_model_s_version_number_corresponding_to_the_last_reload_latest: 64
  format: 2020
  issingleusercloudmodel: F
  last_save_path: C:\Users\hansonje\OneDrive - autodesk\FY-2020 Projects\Revit - 142304 Update Files for 2020\2019 Files\rac_basic_sample_family.rfa
  locale_when_saved: ENU
  model_identity: 00000000-0000-0000-0000-000000000000
  open_workset_default: 3
  project_spark_file: 0
  unique_document_guid: c749ca88-5442-46eb-a706-04db158b688e
  unique_document_increments: 64
  username:
  worksharing: Not enabled

=== Remaining 'garbage' / unparsed lines ===
  $ 00000000-0000-0000-0000-000000000000 ENU Autodesk Revit
```

```
File: racbasicsamplefamily\Contents.bin
Size: 291 bytes

=== Header hexdump (first 0x40 bytes) ===
0000  62 19 22 05 1A 00 00 00 01 00 00 00 02 00 00 00   b.".............
0010  69 64 02 00 00 00 08 00 00 00 01 00 01 00 01 00   id..............
0020  01 00 02 00 02 00 04 00 04 00 04 00 04 00 04 00   ................
0030  04 00 08 00 08 00 08 00 08 00 0A 00 00 00 00 00   ................

=== Header as 32-bit little endian integers ===
  offset 0x0000: 86120802
  offset 0x0004: 26
  offset 0x0008: 1
  offset 0x000C: 2
  offset 0x0010: 156777
  offset 0x0014: 524288
  offset 0x0018: 65536
  offset 0x001C: 65537
  offset 0x0020: 131073
  offset 0x0024: 262146
  offset 0x0028: 262148
  offset 0x002C: 262148
  offset 0x0030: 524292
  offset 0x0034: 524296
  offset 0x0038: 655368
  offset 0x003C: 0

=== Gzip segment found ===
  start offset:      92 (0x005C)
  end offset:        243 (0x00F3)
  compressed size:   151 bytes
  decompressed size: 252 bytes

Decompressed data saved as: racbasicsamplefamily\Contents_decompressed.bin

=== Decompressed hex (first 0x80 bytes) ===
0000  6E 04 01 00 00 00 0C 00 00 00 44 00 61 00 76 00   n.........D.a.v.
0010  69 00 64 00 20 00 43 00 6F 00 6E 00 61 00 6E 00   i.d. .C.o.n.a.n.
0020  74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   t...............
0030  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
0040  00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00   ................
0050  00 00 2D 34 29 35 1E E5 D4 11 92 D8 00 00 86 3F   ..-4)5.........?
0060  27 AD 00 00 00 00 00 00 00 12 00 00 00 32 00 30   '............2.0
0070  00 31 00 39 00 30 00 32 00 30 00 37 00 5F 00 31   .1.9.0.2.0.7._.1

=== UTF-16-LE strings (all alignments) ===
  David Conant
  20190207_1515(x64)

=== ASCII strings from decompressed bytes ===
  -4)5

=== Decoded metadata from Contents ===
  author_candidate: David Conant
  build_candidate:  20190207_1515(x64)
```

```
File: racbasicsamplefamily\Formats_Latest.bin
Size: 142865 bytes

Header hexdump (first 128 bytes):
00000000: 1F 8B 08 00 00 00 00 00 00 0B 8C BA 05 50 55 FD  .............PU.
00000010: 16 3E 0C 4A 0B 88 92 82 B4 4A 0A 48 87 C8 E9 3E  .>.J.....J.H...>
00000020: 1C BA BB 4B 3A 04 E9 EE EE EE EE EE 94 12 91 06  ...K:...........
00000030: E9 10 44 11 09 05 51 24 3E BD EF 7D EF 7D BF FB  ..D...Q$>..}.}..
00000040: CD FF 9B FF 9E D9 33 67 AF 78 D6 F3 5B EB 59 7B  ......3g.x..[.Y{
00000050: E6 9C 39 78 78 14 78 40 11 05 43 47 67 77 20 F2  ..9xx.x@..CGgw .
00000060: B9 A1 B9 29 85 2F DE 7F 4D 38 23 2B 53 63 67 BC  ...)./..M8#+Scg.
00000070: FF 9F EB F6 DF A1 CA 50 F0 5F F9 FF 13 40 F9 8F  .......P._...@..

Decompressed size: 440627 bytes

Decompressed hexdump (first 128 bytes):
00000000: 00 00 0D 00 41 33 50 61 72 74 79 41 49 6D 61 67  ....A3PartyAImag
00000010: 65 0D 80 00 00 0D 00 41 33 50 61 72 74 79 4F 62  e......A3PartyOb
00000020: 6A 65 63 74 00 00 00 00 00 00 00 00 00 00 00 00  ject............
00000030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
00000040: 0F 00 41 33 50 61 72 74 79 53 45 43 49 6D 61 67  ..A3PartySECImag
00000050: 65 0D 00 00 00 00 00 00 00 00 00 00 00 00 00 00  e...............
00000060: 00 0E 00 41 33 50 61 72 74 79 53 45 43 4A 70 65  ...A3PartySECJpe
00000070: 67 0D 00 00 00 00 00 00 00 00 00 00 00 00 00 00  g...............

Length-prefixed ASCII (u16 length) with offsets:
  0x000002: A3PartyAImage
  0x000015: A3PartyObject
  0x000040: A3PartySECImage
  0x000061: A3PartySECJpeg
  0x000081: ACDPtrWrapper
  0x0000AE: ADTGridImportVocabulary
  0x0000CB: ImportVocabulary
  0x000101: std::pair< ElementId, int >
  0x000139: ElementId
  0x00015E: Identifier
  0x0001B4: std::pair< ElementId, double >
  0x000219: std::pair< ElementId, AString >
  0x00027F: std::pair< ElementId, ElementId >
  0x00030F: ADTGridTextLocation
  0x00035C: ADocWarnings
  0x00036E: AppInfo
  0x0003B8: ADocument
  0x000510: DevBranchInfo
  0x0005BA: GUIDvalue
  0x000601: AStringWrapper
  0x004A2B: APIAppInfo
  0x004A59: std::pair< AddInId, AString >
  0x004A93: AddInId
  0x004AD3: APIEventHandlerStatus
  0x004B30: APIVSTAMacroElem
  0x004B46: Element
```

```
File: racbasicsamplefamily\Global_ContentDocuments.bin
Size: 82 bytes

=== Header hexdump (first 0x50 bytes) ===
0000  01 00 00 00 00 00 00 00 1F 8B 08 00 00 00 00 00   ................
0010  00 0B E2 66 66 00 82 FF 40 00 A2 01 00 00 00 FF   ...ff...@.......
0020  FF 02 08 30 00 72 0E 94 B9 0E 00 00 00 00 00 00   ...0.r..........
0030  4C B2 30 63 66 06 20 00 30 D4 42 98 01 90 73 50   L.0cf. .0.B...sP
0040  33 9B 02 B8 9A 39 67 A0 C6 74 8E 79 33 33 00 C1   3....9g..t.y33..

=== Header as 32-bit little endian integers ===
  offset 0x0000: 1
  offset 0x0004: 0
  offset 0x0008: 559903
  offset 0x000C: 0
  offset 0x0010: 1726089984
  offset 0x0014: 4286709862
  offset 0x0018: 27394112
  offset 0x001C: 4278190080
  offset 0x0020: 805831423
  offset 0x0024: 2483974656
  offset 0x0028: 3769
  offset 0x002C: 0
  offset 0x0030: 1664135756
  offset 0x0034: 2098790
  offset 0x0038: 2554516528
  offset 0x003C: 1349750785

=== Header as 16-bit little endian integers ===
  offset 0x0000: 1
  offset 0x0002: 0
  offset 0x0004: 0
  offset 0x0006: 0
  offset 0x0008: 35615
  offset 0x000A: 8
  offset 0x000C: 0
  offset 0x000E: 0
  offset 0x0010: 2816
  offset 0x0012: 26338
  offset 0x0014: 102
  offset 0x0016: 65410
  offset 0x0018: 64
  offset 0x001A: 418
  offset 0x001C: 0
  offset 0x001E: 65280
  offset 0x0020: 767
  offset 0x0022: 12296
  offset 0x0024: 29184
  offset 0x0026: 37902
  offset 0x0028: 3769
  offset 0x002A: 0
  offset 0x002C: 0
  offset 0x002E: 0
  offset 0x0030: 45644
  offset 0x0032: 25392
  offset 0x0034: 1638
  offset 0x0036: 32
  offset 0x0038: 54320
  offset 0x003A: 38978
  offset 0x003C: 36865
  offset 0x003E: 20595

=== Gzip segment found ===
  start offset:      8 (0x0008)
  end offset:        48 (0x0030)
  compressed size:   40 bytes
  decompressed size: 14 bytes
```

```
File: racbasicsamplefamily\Global_DocumentIncrementTable.bin
Size: 1650 bytes

=== Header hexdump (first 0x80 bytes) ===
0000  01 00 00 00 00 00 00 00 1F 8B 08 00 00 00 00 00   ................
0010  00 0B EC 99 5D 4C 5C 45 14 C7 67 61 77 F9 5C 28   ....]L\\E..gaw.\\(
0020  6D A1 5A 48 40 B4 82 45 6D A1 D4 96 42 71 F9 92   m.ZH@..Em...Bq..
0030  6E B0 A9 95 6A 11 2B DF 74 97 76 81 16 16 04 6A   n...j.+.t.v....j
0040  B7 C5 DA 36 FA 60 8D 26 3E A9 89 C6 8F C4 F8 52   ...6.`.&>......R
0050  35 7D D1 F4 C1 9A F6 09 BF 52 4D 8A B1 26 FA A0   5}.......RM..&..
0060  89 DA D6 37 13 35 78 CE EC CC DE 73 A7 7B 81 C2   ...7.5x....s.{..
0070  EE 4D 4C 66 C8 7F 99 D9 73 F6 FC 66 EE 9D 3B 3B   .MLf....s..f..;;

=== Header as 32-bit little endian integers ===
  offset 0x0000: 1
  offset 0x0004: 0
  offset 0x0008: 559903
  offset 0x000C: 0
  offset 0x0010: 2582383360
  offset 0x0014: 1163676765
  offset 0x0018: 1634191124
  offset 0x001C: 677181815
  offset 0x0020: 1213899117
  offset 0x0024: 1166193728
  offset 0x0028: 2530517357
  offset 0x002C: 2465820994
  offset 0x0030: 2510925934
  offset 0x0034: 3744141674
  offset 0x0038: 2172032884
  offset 0x003C: 1778652694

=== Header as 16-bit little endian integers ===
  offset 0x0000: 1
  offset 0x0002: 0
  offset 0x0004: 0
  offset 0x0006: 0
  offset 0x0008: 35615
  offset 0x000A: 8
  offset 0x000C: 0
  offset 0x000E: 0
  offset 0x0010: 2816
  offset 0x0012: 39404
  offset 0x0014: 19549
  offset 0x0016: 17756
  offset 0x0018: 50964
  offset 0x001A: 24935
  offset 0x001C: 63863
  offset 0x001E: 10332
  offset 0x0020: 41325
  offset 0x0022: 18522
  offset 0x0024: 46144
  offset 0x0026: 17794
  offset 0x0028: 41325
  offset 0x002A: 38612
  offset 0x002C: 28994
  offset 0x002E: 37625
  offset 0x0030: 45166
  offset 0x0032: 38313
  offset 0x0034: 4458
  offset 0x0036: 57131
  offset 0x0038: 38772
  offset 0x003A: 33142
  offset 0x003C: 5654
  offset 0x003E: 27140

=== Gzip segment found ===
  start offset:      8 (0x0008)
  end offset:        1575 (0x0627)
  compressed size:   1567 bytes
  decompressed size: 14498 bytes

Decompressed data saved as: racbasicsamplefamily\Global_DocumentIncrementTable_decompressed.bin

=== Decompressed hex (first 0x80 bytes) ===
0000  6C 04 40 00 00 00 01 00 00 00 22 00 00 00 00 00   l.@.......".....
0010  00 00 00 00 00 00 00 00 00 00 28 00 00 00 00 00   ..........(.....
0020  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
0030  00 00 FF FF FF FF FF FF FF FF FF FF FF FF FF FF   ................
0040  FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF   ................
0050  FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF   ................
0060  FF FF 00 01 00 00 00 22 00 00 00 00 00 00 00 0C   ......."........
0070  00 00 00 44 00 61 00 76 00 69 00 64 00 20 00 43   ...D.a.v.i.d. .C

=== Decompressed as 32-bit little endian integers (first 16) ===
  offset 0x0000: 4195436
  offset 0x0004: 65536
  offset 0x0008: 2228224
  offset 0x000C: 0
  offset 0x0010: 0
  offset 0x0014: 0
  offset 0x0018: 2621440
  offset 0x001C: 0
  offset 0x0020: 0
  offset 0x0024: 0
  offset 0x0028: 0
  offset 0x002C: 0
  offset 0x0030: 4294901760
  offset 0x0034: 4294967295
  offset 0x0038: 4294967295
  offset 0x003C: 4294967295

=== Decompressed as (uint32, uint32) pairs (first 16) ===
  offset 0x0000: (4195436, 65536)
  offset 0x0008: (2228224, 0)
  offset 0x0010: (0, 0)
  offset 0x0018: (2621440, 0)
  offset 0x0020: (0, 0)
  offset 0x0028: (0, 0)
  offset 0x0030: (4294901760, 4294967295)
  offset 0x0038: (4294967295, 4294967295)
  offset 0x0040: (4294967295, 4294967295)
  offset 0x0048: (4294967295, 4294967295)
  offset 0x0050: (4294967295, 4294967295)
  offset 0x0058: (4294967295, 4294967295)
  offset 0x0060: (16842751, 570425344)
  offset 0x0068: (0, 201326592)
  offset 0x0070: (1140850688, 1979736320)
  offset 0x0078: (1677748480, 1124081664)

=== UTF-16-LE strings (all alignments) ===
  Sacha Silva
  Steven Campbell
  Erik Egbertson
  campbes
  demchag
  conantd
  Steve Crotty
  lannent
  tpartner
  heka
  guanq
  hansonje
  suju
  youyi
  loboarch
  David Conant
  crottys
  smithl
  dobriai
  lixi
  duboism
  wangmin
  t_zhoum
```

```
File: racbasicsamplefamily\Global_ElemTable.bin
Size: 7224 bytes

File hexdump (first 256 bytes):
00000000: 00 00 00 00 00 00 00 00 1F 8B 08 00 00 00 00 00  ................
00000010: 00 0B 74 DD 05 94 6D 55 FD C0 F1 79 74 CE 9C C7  ..t...mU...yt...
00000020: 8D B3 CF D9 9B EE EE 6E 10 10 30 08 11 0C 14 29  .......n..0....)
00000030: 11 41 29 A5 3B ED C2 96 06 09 09 69 09 03 4C 14  .A).;......i..L.
00000040: 30 68 A4 BB 5B 40 40 F8 BF FD FF EE 59 33 1E BF  0h..[@@.....Y3..
00000050: DC B5 3E EB AD B7 BF BF 7D CE BD 73 EF DC A9 77  ..>.....}..s...w
00000060: E7 DD 33 C3 ED 33 8D BC EB 65 EA 34 53 8A 75 27  ..3..3...e.4S.u'
00000070: 19 BF 4C 5F 58 9B A1 B0 63 CE 58 58 9B A9 B0 36  ..L_X...c.XX...6
00000080: 73 61 6D 96 C2 DA AC 85 B5 D9 0A 6B B3 17 D6 E6  sam........k....
00000090: 28 BA B7 3D CF 8F 16 B6 6F AC E8 EE 1B 2D 7D 6A  (..=....o....-}j
000000A0: F9 FB B1 45 BE BC 33 ED 32 D7 B4 3F E7 7A 97 63  ...E..3.2..?.z.c
000000B0: F6 8A EE 31 F3 FC A0 C8 97 A3 A6 D9 64 D2 BE 61  ...1........d..a
000000C0: 91 2F 87 4D 6A F5 24 B6 2F 14 DD 4B 9E 6F 8A CD  ./.Mj.$./..K.o..
000000D0: 26 19 29 F3 6D D1 3D 5F 9C C4 CE 97 8A EE 25 CF  &.).m.=_......%.
000000E0: CF 5D 74 CF 97 E7 E7 29 C6 CF 37 7E 99 77 12 3B  .]t....)..7~.w.;
000000F0: DF 7C 45 F7 92 E7 E7 2F BA E7 CB F3 0B 14 DD F3  .|E..../........

Prefix u32[0]: 0
Prefix u32[1]: 0

GZip offset: 8

GZip header:
  cm: 8
  flg: 0x00
  mtime: 0
  xfl: 0
  os: 11

Decompressed size: 49457 bytes
GZip trailer crc32: 0x8BDF261A
GZip trailer isize: 49457
Computed crc32: 0x8BDF261A

Decompressed hexdump (first 256 bytes):
00000000: DC 04 D6 06 00 00 00 00 00 00 00 00 00 00 00 00  ................
00000010: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 00  ................
00000020: 00 00 01 00 00 00 01 00 00 00 3F 00 00 00 3F 00  ..........?...?.
00000030: 00 00 3F 00 00 00 00 00 00 00 00 00 00 00 03 00  ..?.............
00000040: 00 00 03 00 00 00 3F 00 00 00 3F 00 00 00 3F 00  ......?...?...?.
00000050: 00 00 00 00 00 00 00 00 00 00 04 00 00 00 04 00  ................
00000060: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
00000070: 00 00 11 00 00 00 05 00 00 00 05 00 00 00 00 00  ................
00000080: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 00  ................
00000090: 00 00 06 00 00 00 06 00 00 00 00 00 00 00 00 00  ................
000000A0: 00 00 00 00 00 00 00 00 00 00 11 00 00 00 07 00  ................
000000B0: 00 00 07 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000000C0: 00 00 00 00 00 00 11 00 00 00 08 00 00 00 08 00  ................
000000D0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000000E0: 00 00 11 00 00 00 09 00 00 00 09 00 00 00 00 00  ................
000000F0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 11 00  ................
```

```
PNG preview saved as: racbasicsamplefamily\RevitPreview4.0.png
Size: 1133 bytes
```
