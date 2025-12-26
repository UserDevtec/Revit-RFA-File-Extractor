# Extract-RFA-file

Extracts and decodes metadata from Revit `.rfa` files, including the `BasicFileInfo.bin` content.

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
