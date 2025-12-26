import argparse
import json
import pathlib
import re
import sys

STDOUT_ENCODING = sys.stdout.encoding or "utf-8"


def safe_print(text=""):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(STDOUT_ENCODING, "backslashreplace").decode(STDOUT_ENCODING))


def asciiish_from_utf16(blob: bytes, endian: str) -> str:
    txt = blob.decode("utf-16-" + endian, errors="ignore")
    out = []
    for ch in txt:
        code = ord(ch)
        if ch in "\r\n":
            out.append("\n")
        elif 32 <= code <= 126:
            out.append(ch)
        else:
            out.append(" ")
    s = "".join(out)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n+", "\n", s)
    return s.strip()


def parse_kv_lines(lines):
    meta = {}
    leftovers = []

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            snake = re.sub(r"[^0-9a-zA-Z]+", "_", key).strip("_").lower()
            meta[snake] = value
        else:
            leftovers.append(line)

    if "orksharing" in meta and "worksharing" not in meta:
        meta["worksharing"] = meta.pop("orksharing")

    return meta, leftovers


def main():
    parser = argparse.ArgumentParser(
        description="Decode and show EVERYTHING from BasicFileInfo.bin"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily/BasicFileInfo.bin",
        help="Default: racbasicsamplefamily/BasicFileInfo.bin",
    )
    parser.add_argument(
        "--json-out",
        action="store_true",
        help="Write parsed metadata JSON next to bin",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    blob = path.read_bytes()

    safe_print(f"File: {path}")
    safe_print(f"Size: {len(blob)} bytes\n")

    # --- decode both ---
    clean_le = asciiish_from_utf16(blob, "le")
    clean_be = asciiish_from_utf16(blob, "be")

    # --- split to lines ---
    be_lines = [ln for ln in clean_be.split("\n") if ln.strip()]
    le_lines = [ln for ln in clean_le.split("\n") if ln.strip()]

    # --- parse BE key/values ---
    meta, leftovers = parse_kv_lines(be_lines)

    # Add fallback format from LE
    if "format" not in meta:
        m = re.search(r"\b(\d{4})\b", clean_le)
        if m:
            meta["format"] = m.group(1)

    # -------------------------
    # PRINT EVERYTHING CLEANLY
    # -------------------------

    safe_print("=== UTF-16 BE decoded (ASCII-ish) ===")
    safe_print(clean_be + "\n")

    safe_print("=== UTF-16 LE decoded (ASCII-ish) ===")
    safe_print(clean_le + "\n")

    safe_print("=== Parsed Key/Value fields ===")
    for k in sorted(meta.keys()):
        safe_print(f"  {k}: {meta[k]}")
    safe_print()

    safe_print("=== Remaining 'garbage' / unparsed lines ===")
    if leftovers:
        for ln in leftovers:
            safe_print(f"  {ln}")
    else:
        safe_print("  <none>")
    safe_print()

    # Optional JSON file
    if args.json_out:
        json_path = path.with_name(path.stem + "_decoded.json")
        json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        safe_print(f"JSON written: {json_path}")


if __name__ == "__main__":
    main()
