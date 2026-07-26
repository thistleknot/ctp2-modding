# Protected Files Contract

This file is a first-class commit gate. Read it before touching CTP2 UI or image
assets.

## Do Not Touch

Do not hand-edit, delete, replace, regenerate, or scenario-shadow the protected
base picture surface:

```text
ctp2_data\default\graphics\pictures\**\*.tga
ctp2_data\default\graphics\pictures\pic555.zfs
ctp2_data\default\graphics\pictures\pic565.zfs
ctp2_data\default\graphics\pictures\badTGA.txt
ctp2_program\ctp\**\*
```

For this workspace, the canonical sources for that surface are:

```text
H:\Program Files(x86)\Activision\Call To Power 2 - ae\ctp2_data\default\graphics\pictures\**\*.tga
H:\Program Files(x86)\Activision\Call To Power 2 - Copy\ctp2_data\default\graphics\pictures\pic555.zfs
H:\Program Files(x86)\Activision\Call To Power 2 - Copy\ctp2_data\default\graphics\pictures\pic565.zfs
H:\Program Files(x86)\Activision\Call To Power 2 - Copy\ctp2_data\default\graphics\pictures\badTGA.txt
H:\Program Files(x86)\Activision\Call To Power 2 - Copy\ctp2_program\ctp\**\*
```

The manifest also includes generated LDL-reference closure files when every local
baseline is missing the exact filename but stock LDLs require it. The known closure
families are `uptg06a.tga` through `uptg06i.tga`, generated from the sibling
`uptg07*` family plus `uptg06f-2.tga`, and the Ranger arrow files
`upba5614.tga`, `upba5615.tga`, `upba6322.tga`, and `upba6324.tga`.

## Commit Rule

Every commit that changes CTP2 UI/image behavior must include:

1. `PROTECTED_FILES.md`
2. `verify_protected_files.py`
3. `protected_files_manifest.tsv`
4. `ctp_program_manifest.tsv`
5. every protected picture file required by `protected_files_manifest.tsv`
6. every protected program file required by `ctp_program_manifest.tsv`

Do not commit partial family fixes such as only `upbt01*`, only `upbt06*`, only
`uptg06*`, or only `upsg*`. The protected surface is the whole manifest under the
matching base path.

## Validation Rule

Run this before committing:

```powershell
python verify_protected_files.py
```

Expected result:

```text
protected_manifest_entries=2638
ctp_program_manifest_entries=48
missing_files=0
hash_mismatches=0
mom_shadow_files=0
ctp_program_missing_files=0
ctp_program_hash_mismatches=0
ctp_program_extra_files=0
missing_nonallowlisted_ldl_tga_refs=0
unstaged_or_untracked_protected_files=0
```

If any count is non-zero, the commit is not ready.

## Why This Exists

The May 2026 UI regression was caused by repeatedly fixing one named TGA family at
a time. That under-branched from the evidence. The correct boundary is not
`upbt01*`, `uptg06*`, `upsg*`, or loose `.tga` files only; it is all protected
picture files under the same base picture path, including packed `pic555.zfs` and
`pic565.zfs`, the entire Copy-canonical `ctp2_program\ctp` tree,
manifest-owned generated closure files, plus zero MoM scenario shadows for those
protected names.
