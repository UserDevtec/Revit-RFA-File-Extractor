import argparse
import gzip
import pathlib
import re
import struct
import sys

STDOUT_ENCODING = sys.stdout.encoding or "utf-8"


def safe_print(text: str = ""):
    """Print without the console crashing on odd Unicode."""
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode(
            STDOUT_ENCODING, errors="backslashreplace"
        ).decode(STDOUT_ENCODING, errors="backslashreplace")
        print(safe)


def hex_dump(b: bytes, width: int = 16, limit: int | None = None) -> str:
    """Simple hexdump helper."""
    if limit is not None:
        b = b[:limit]
    lines = []
    for i in range(0, len(b), width):
        chunk = b[i : i + width]
        hexs = " ".join(f"{x:02X}" for x in chunk)
        ascii_s = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        lines.append(f"{i:04X}  {hexs:<{width*3}}  {ascii_s}")
    return "\n".join(lines)


def parse_header_uint32_le(blob: bytes, max_count: int = 16):
    """Interpret the first bytes as 32-bit little endian integers."""
    count = min(max_count, len(blob) // 4)
    entries = []
    for i in range(count):
        off = i * 4
        val = struct.unpack_from("<I", blob, off)[0]
        entries.append((off, val))
    return entries


def ascii_strings_from_bytes(blob: bytes, min_len: int = 4):
    """Search for normal ASCII strings in raw bytes."""
    results = []
    current = bytearray()

    def flush():
        nonlocal current
        if len(current) >= min_len:
            results.append(current.decode("ascii", errors="ignore"))
        current = bytearray()

    for b in blob:
        if 32 <= b <= 126:
            current.append(b)
        else:
            flush()
    flush()
    return results


def extract_utf16le_strings_all_alignments(blob: bytes, min_len: int = 4):
    """
    Search for UTF-16LE strings while trying both possible alignments
    (offset 0 and 1). This finds both 'David Conant'
    and '20190207_1515(x64)'.
    """
    results = []

    for start_offset in (0, 1):
        current = []

        def flush():
            nonlocal current
            if len(current) >= min_len:
                results.append("".join(current))
            current = []

        i = start_offset
        while i + 1 < len(blob):
            ch = blob[i]
            nul = blob[i + 1]
            if 32 <= ch <= 126 and nul == 0:
                current.append(chr(ch))
            else:
                flush()
            i += 2
        flush()

    # remove duplicates
    dedup = []
    seen = set()
    for s in results:
        if s not in seen:
            seen.add(s)
            dedup.append(s)
    return dedup


def find_and_decompress_gzip(blob: bytes):
    """
    Search for a gzip header (1F 8B 08) in the blob and try to
    decompress it by moving the end backward until gzip.decompress
    succeeds. Returns (start, end, decompressed_bytes) or (None, None, None).
    """
    magic = b"\x1f\x8b\x08"

    for i in range(len(blob) - 2):
        if blob[i : i + 3] != magic:
            continue

        # move the end backward until gzip.decompress succeeds
        for end in range(len(blob), i + 10, -1):
            chunk = blob[i:end]
            try:
                decomp = gzip.decompress(chunk)
                return i, end, decomp
            except Exception:
                continue

    return None, None, None


def main():
    parser = argparse.ArgumentParser(
        description="Decode racbasicsamplefamily/Contents.bin (header + gzip + strings)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily/Contents.bin",
        help="Path to Contents.bin (default: racbasicsamplefamily/Contents.bin)",
    )
    parser.add_argument(
        "--dump-hex",
        action="store_true",
        help="Show full hexdump of Contents.bin",
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

    # 1. Header analysis
    safe_print("=== Header hexdump (first 0x40 bytes) ===")
    safe_print(hex_dump(blob[:0x40]))
    safe_print()

    safe_print("=== Header as 32-bit little endian integers ===")
    for off, val in parse_header_uint32_le(blob[:0x40]):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    if args.dump_hex:
        safe_print("=== Full hexdump of Contents.bin ===")
        safe_print(hex_dump(blob))
        safe_print()

    # 2. Find gzip segment
    start, end, decomp = find_and_decompress_gzip(blob)
    if decomp is None:
        safe_print("No valid gzip segment found in Contents.bin")
        return 0

    safe_print("=== Gzip segment found ===")
    safe_print(f"  start offset:      {start} (0x{start:04X})")
    safe_print(f"  end offset:        {end} (0x{end:04X})")
    safe_print(f"  compressed size:   {end - start} bytes")
    safe_print(f"  decompressed size: {len(decomp)} bytes")
    safe_print()

    # 3. Write decompressed data
    out_path = path.with_name("Contents_decompressed.bin")
    out_path.write_bytes(decomp)
    safe_print(f"Decompressed data saved as: {out_path}")
    safe_print()

    # 4. Hexdump of decompressed data
    safe_print("=== Decompressed hex (first 0x80 bytes) ===")
    safe_print(hex_dump(decomp, limit=0x80))
    safe_print()

    # 5. Strings from decompressed bytes
    utf16_strings = extract_utf16le_strings_all_alignments(decomp, min_len=4)
    ascii_strings = ascii_strings_from_bytes(decomp, min_len=4)

    safe_print("=== UTF-16-LE strings (all alignments) ===")
    if utf16_strings:
        for s in utf16_strings:
            safe_print(f"  {s}")
    else:
        safe_print("  <none>")
    safe_print()

    safe_print("=== ASCII strings from decompressed bytes ===")
    if ascii_strings:
        for s in ascii_strings:
            safe_print(f"  {s}")
    else:
        safe_print("  <none>")
    safe_print()

    # 6. Best guess: author + build from UTF-16 strings
    author = utf16_strings[0] if utf16_strings else None
    build = None
    for s in utf16_strings:
        m = re.search(r"\b20[0-9]{6}_[0-9]{4}\(x[0-9]+\)", s)
        if m:
            build = m.group(0)
            break

    safe_print("=== Decoded metadata from Contents ===")
    if author:
        safe_print(f"  author_candidate: {author}")
    if build:
        safe_print(f"  build_candidate:  {build}")
    if not author and not build:
        safe_print("  <no extra metadata found>")
    safe_print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
