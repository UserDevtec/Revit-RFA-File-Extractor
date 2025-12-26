import argparse
import json
import locale
import pathlib
import re
import sys

STDOUT_ENCODING = sys.stdout.encoding or "utf-8"
BASE_DEFAULT = pathlib.Path("racbasicsamplefamily") / "BasicFileInfo.bin"


def safe_print(text: str = ""):
    """Print text without the console breaking on odd Unicode."""
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode(
            STDOUT_ENCODING, errors="backslashreplace"
        ).decode(STDOUT_ENCODING, errors="backslashreplace")
        print(safe)


def extract_utf16le_strings(blob: bytes, min_len: int = 4):
    """Scan blob as UTF-16 LE and collect readable substrings."""
    results = []
    current = []

    def flush():
        if len(current) >= min_len:
            results.append("".join(current))
        current.clear()

    i = 0
    while i + 1 < len(blob):
        ch = blob[i]
        nul = blob[i + 1]
        if 32 <= ch <= 126 and nul == 0:
            current.append(chr(ch))
        else:
            flush()
        i += 2

    flush()
    return results


def decode_full_utf16le(blob: bytes):
    """Full UTF-16 LE decode with cleanup into individual lines."""
    text = blob.decode("utf-16-le", errors="ignore")
    text = text.replace("\x00", "")
    lines = [line.strip() for line in text.replace("\r", "").split("\n")]
    return [line for line in lines if line]


def extract_guids(text: str):
    pattern = re.compile(
        r"[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{12}"
    )
    return sorted(set(pattern.findall(text)))


def parse_metadata_from_lines(lines):
    """
    Heuristics to extract the key fields from BasicFileInfo.
    Works well for your example and usually for other Revit files too.
    """
    info: dict[str, object] = {}
    joined = " ".join(lines)
    tokens = joined.split()

    # Revit version: first token with exactly 4 digits
    for t in tokens:
        if re.fullmatch(r"\d{4}", t):
            info["revit_version"] = t
            break

    # Build string: something like 20190207_1515(x64)
    for t in tokens:
        if "_" in t and "(" in t and ")" in t:
            info["build"] = t
            break

    # Original file path
    original_path = ""
    for i, t in enumerate(tokens):
        if ":" in t and "\\" in t:
            parts = [t]
            for u in tokens[i + 1 :]:
                parts.append(u)
                if u.lower().endswith((".rfa", ".rvt")):
                    break
            original_path = " ".join(parts)
            break
    if original_path:
        info["original_path"] = original_path

    # GUIDs
    guids = extract_guids(joined)
    if guids:
        info["document_guid"] = guids[0]
        if len(guids) > 1:
            info["session_guid"] = guids[1]
        if len(guids) > 2:
            info["extra_guids"] = guids[2:]

    # Platform bits: something like 64$
    for t in tokens:
        if t.endswith("$") and t[:-1].isdigit():
            try:
                info["platform_bits"] = int(t[:-1])
            except ValueError:
                pass
            break

    return info


def main():
    parser = argparse.ArgumentParser(
        description="Decode racbasicsamplefamily/BasicFileInfo.bin"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=str(BASE_DEFAULT),
        help="Path to BasicFileInfo.bin "
        "(default: racbasicsamplefamily/BasicFileInfo.bin)",
    )
    parser.add_argument(
        "--dump-lines",
        action="store_true",
        help="Show all UTF-16 LE lines",
    )
    parser.add_argument(
        "--dump-substrings",
        action="store_true",
        help="Dump all found UTF-16 substrings",
    )
    parser.add_argument(
        "--json-out",
        action="store_true",
        help="Write metadata to BasicFileInfo.json next to the bin",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    if not path.exists():
        safe_print(f"File not found: {path}")
        return 1

    blob = path.read_bytes()
    safe_print(f"File: {path}")
    safe_print(f"Size: {len(blob)} bytes")
    safe_print()

    # Full decode to lines
    lines = decode_full_utf16le(blob)

    # Extract metadata
    meta = parse_metadata_from_lines(lines)

    safe_print("Parsed metadata:")
    safe_print("----------------")
    for key in sorted(meta.keys()):
        safe_print(f"  {key}: {meta[key]}")
    safe_print()

    if args.json_out:
        json_path = path.with_suffix(".json")
        json_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        safe_print(f"Metadata written to: {json_path}")
        safe_print()

    # Optional: dump all UTF-16 LE lines
    if args.dump_lines:
        safe_print("UTF-16LE lines (full decode):")
        safe_print("--------------------------------")
        for line in lines:
            safe_print(f"  {line}")
        safe_print()

    # Optional: brute-force substring scan
    if args.dump_substrings:
        safe_print("Extracted UTF-16LE substrings (scan):")
        safe_print("-------------------------------------")
        for s in extract_utf16le_strings(blob):
            safe_print(f"  {s}")
        safe_print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
