import argparse
import pathlib
import re
import sys

STDOUT_ENCODING = sys.stdout.encoding or 'utf-8'


def safe_print(text: str = ""):
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode(STDOUT_ENCODING, errors="backslashreplace").decode(
            STDOUT_ENCODING, errors="backslashreplace"
        )
        print(safe)


def extract_utf16le_strings(blob: bytes, min_len: int = 4):
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


def decode_length_prefixed_utf16le(blob: bytes, max_len: int = 4096):
    results = []
    i = 0
    while i + 4 <= len(blob):
        length = int.from_bytes(blob[i : i + 4], "little")
        i += 4
        if length == 0:
            results.append("")
            continue
        if length > max_len:
            break
        byte_len = length * 2
        if i + byte_len > len(blob):
            break
        chunk = blob[i : i + byte_len]
        i += byte_len
        try:
            s = chunk.decode("utf-16-le", errors="strict")
        except UnicodeDecodeError:
            s = chunk.decode("utf-16-le", errors="ignore")
        printable = sum(1 for c in s if 32 <= ord(c) <= 126)
        ratio = printable / max(1, len(s))
        if ratio >= 0.6:
            results.append(s)
        else:
            results.append(s)
    return results


def decode_full_utf16le(blob: bytes):
    text = blob.decode("utf-16-le", errors="ignore")
    text = text.replace("\x00", "")
    lines = [line.strip() for line in text.replace("\r", "").split("\n")]
    return [line for line in lines if line]


def clean_line(line: str):
    cleaned = []
    for ch in line:
        code = ord(ch)
        if ch in "\t " or 32 <= code <= 126:
            cleaned.append(ch)
    return "".join(cleaned).strip()


def extract_paths(lines):
    paths = []
    for line in lines:
        if ":\\" in line or ":/" in line:
            paths.append(line)
    return paths


def extract_guids(text: str):
    pattern = re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )
    return sorted(set(pattern.findall(text)))


def main():
    parser = argparse.ArgumentParser(
        description="Decode BasicFileInfo.bin from an RFA unpack."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily\BasicFileInfo.bin",
        help="Path to BasicFileInfo.bin",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    if not path.exists():
        safe_print(f"File not found: {path}")
        return 1

    blob = path.read_bytes()
    output_lines = []

    def emit(text: str = ""):
        safe_print(text)
        output_lines.append(text)

    emit(f"File: {path}")
    emit(f"Size: {len(blob)} bytes")
    emit()

    emit("Length-prefixed UTF-16LE strings (cleaned):")
    for s in decode_length_prefixed_utf16le(blob):
        cleaned = clean_line(s)
        if cleaned:
            emit(f"  {cleaned}")
    emit()

    emit("UTF-16LE lines (cleaned):")
    raw_lines = decode_full_utf16le(blob)
    lines = []
    for line in raw_lines:
        cleaned = clean_line(line)
        if cleaned:
            lines.append(cleaned)
            emit(f"  {cleaned}")
    emit()

    emit("Key/Value lines (clean):")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            emit(f"  {key}: {value}")
    emit()

    joined = "\n".join(lines)
    guids = extract_guids(joined)
    if guids:
        emit("GUIDs:")
        for g in guids:
            emit(f"  {g}")
        emit()

    paths = extract_paths(lines)
    if paths:
        emit("Paths:")
        for p in sorted(set(paths)):
            emit(f"  {p}")
        emit()

    emit("Extracted UTF-16LE substrings (cleaned scan):")
    for s in extract_utf16le_strings(blob):
        cleaned = clean_line(s)
        if cleaned:
            emit(f"  {cleaned}")

    output_dir = pathlib.Path(__file__).resolve().parent
    output_path = output_dir / f"{path.stem}_Leesbaar.txt"
    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    emit()
    emit(f"Saved: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
