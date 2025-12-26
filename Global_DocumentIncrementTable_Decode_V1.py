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
        alt = text.encode(
            STDOUT_ENCODING, errors="backslashreplace"
        ).decode(STDOUT_ENCODING, errors="backslashreplace")
        print(alt)


def hex_dump(data: bytes, width: int = 16, limit: int | None = None) -> str:
    """Simple hexdump helper."""
    if limit is not None:
        data = data[:limit]
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i : i + width]
        hexs = " ".join(f"{b:02X}" for b in chunk)
        ascii_s = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"{i:04X}  {hexs:<{width*3}}  {ascii_s}")
    return "\n".join(lines)


def parse_uints_le(blob: bytes, unit: int, max_count: int):
    """
    Interpret the first bytes as little endian integers:
    unit = 2 (uint16) or 4 (uint32).
    """
    count = min(max_count, len(blob) // unit)
    vals = []
    fmt = "<H" if unit == 2 else "<I"
    for i in range(count):
        off = i * unit
        val = struct.unpack_from(fmt, blob, off)[0]
        vals.append((off, val))
    return vals


def ascii_strings_from_bytes(blob: bytes, min_len: int = 4):
    """Search for normal ASCII strings in raw bytes."""
    results = []
    cur = bytearray()

    def flush():
        nonlocal cur
        if len(cur) >= min_len:
            results.append(cur.decode("ascii", errors="ignore"))
        cur = bytearray()

    for b in blob:
        if 32 <= b <= 126:
            cur.append(b)
        else:
            flush()
    flush()
    return results


def utf16le_strings_all_alignments(blob: bytes, min_len: int = 4):
    """
    Search for UTF-16LE strings at both possible alignments (offset 0 and 1).
    This captures as much readable text as possible.
    """
    results = []

    for start in (0, 1):
        cur = []

        def flush():
            nonlocal cur
            if len(cur) >= min_len:
                results.append("".join(cur))
            cur = []

        i = start
        while i + 1 < len(blob):
            ch = blob[i]
            nul = blob[i + 1]
            if 32 <= ch <= 126 and nul == 0:
                cur.append(chr(ch))
            else:
                flush()
            i += 2
        flush()

    # dedup
    uniq = []
    seen = set()
    for s in results:
        if s not in seen:
            uniq.append(s)
            seen.add(s)
    return uniq


def extract_guids(text: str):
    pat = re.compile(
        r"[0-9A-Fa-f]{8}-"
        r"[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{4}-"
        r"[0-9A-Fa-f]{12}"
    )
    return sorted(set(pat.findall(text)))


def find_and_decompress_gzip(blob: bytes):
    """
    Search for a gzip header (1F 8B 08) and try to decompress a valid
    gzip block by moving the end backward.

    Returns (start_offset, end_offset, decompressed_bytes)
    or (None, None, None) if nothing succeeds.
    """
    magic = b"\x1f\x8b\x08"

    for start in range(len(blob) - 2):
        if blob[start : start + 3] != magic:
            continue

        # move the end backward until gzip.decompress succeeds
        for end in range(len(blob), start + 10, -1):
            chunk = blob[start:end]
            try:
                decomp = gzip.decompress(chunk)
                return start, end, decomp
            except Exception:
                continue

    return None, None, None


def inspect_uint32_pairs(decomp: bytes, max_pairs: int = 16):
    """
    Interpret decompressed data as a table of (uint32, uint32) pairs.
    Handy for something called 'DocumentIncrementTable'.
    """
    pairs = []
    pair_size = 8
    total_pairs = min(max_pairs, len(decomp) // pair_size)
    for i in range(total_pairs):
        off = i * pair_size
        a, b = struct.unpack_from("<II", decomp, off)
        pairs.append((off, a, b))
    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Decode racbasicsamplefamily/Global_DocumentIncrementTable.bin"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily/Global_DocumentIncrementTable.bin",
        help="Path to Global_DocumentIncrementTable.bin "
             "(default: racbasicsamplefamily/Global_DocumentIncrementTable.bin)",
    )
    parser.add_argument(
        "--dump-hex",
        action="store_true",
        help="Show full hexdump of the source file",
    )
    args = parser.parse_args()

    path = pathlib.Path(args.path)
    if not path.exists():
        safe_print(f"File not found: {path}")
        return 1

    blob = path.read_bytes()

    safe_print(f"File: {path}")
    safe_print(f"Size: {len(blob)} bytes\n")

    # 1. Header analysis
    safe_print("=== Header hexdump (first 0x80 bytes) ===")
    safe_print(hex_dump(blob[:0x80]))
    safe_print()

    safe_print("=== Header as 32-bit little endian integers ===")
    for off, val in parse_uints_le(blob[:0x80], unit=4, max_count=16):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    safe_print("=== Header as 16-bit little endian integers ===")
    for off, val in parse_uints_le(blob[:0x80], unit=2, max_count=32):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    if args.dump_hex:
        safe_print("=== Full hexdump of Global_DocumentIncrementTable.bin ===")
        safe_print(hex_dump(blob))
        safe_print()

    # 2. Find gzip segment and decompress
    start, end, decomp = find_and_decompress_gzip(blob)
    if decomp is None:
        safe_print("No valid gzip segment found in Global_DocumentIncrementTable.bin")
        return 0

    safe_print("=== Gzip segment found ===")
    safe_print(f"  start offset:      {start} (0x{start:04X})")
    safe_print(f"  end offset:        {end} (0x{end:04X})")
    safe_print(f"  compressed size:   {end - start} bytes")
    safe_print(f"  decompressed size: {len(decomp)} bytes")
    safe_print()

    # 3. Write decompressed data
    out_path = path.with_name("Global_DocumentIncrementTable_decompressed.bin")
    out_path.write_bytes(decomp)
    safe_print(f"Decompressed data saved as: {out_path}")
    safe_print()

    # 4. Decompressed hexdump
    safe_print("=== Decompressed hex (first 0x80 bytes) ===")
    safe_print(hex_dump(decomp, limit=0x80))
    safe_print()

    safe_print("=== Decompressed as 32-bit little endian integers (first 16) ===")
    for off, val in parse_uints_le(decomp, unit=4, max_count=16):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    # 5. Table of uint32 pairs (assumption: doc_id / increment)
    safe_print("=== Decompressed as (uint32, uint32) pairs (first 16) ===")
    pairs = inspect_uint32_pairs(decomp, max_pairs=16)
    if pairs:
        for off, a, b in pairs:
            safe_print(f"  offset 0x{off:04X}: ({a}, {b})")
    else:
        safe_print("  <not enough data for pairs>")
    safe_print()

    # 6. Strings and GUIDs from decompressed data
    utf16 = utf16le_strings_all_alignments(decomp, min_len=4)
    ascii_s = ascii_strings_from_bytes(decomp, min_len=4)

    safe_print("=== UTF-16-LE strings (all alignments) ===")
    if utf16:
        for s in utf16:
            safe_print(f"  {s}")
    else:
        safe_print("  <none>")
    safe_print()

    safe_print("=== ASCII strings ===")
    if ascii_s:
        for s in ascii_s:
            safe_print(f"  {s}")
    else:
        safe_print("  <none>")
    safe_print()

    joined = "\n".join(utf16 + ascii_s)
    guids = extract_guids(joined)

    safe_print("=== Possible GUIDs in decompressed data ===")
    if guids:
        for g in guids:
            safe_print(f"  {g}")
    else:
        safe_print("  <none>")
    safe_print()

    safe_print(
        "Note: the shown integers/pairs most likely form a document-increment "
        "table (indices/version numbers), but the exact meaning requires "
        "knowledge of the internal Revit format."
    )
    safe_print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
