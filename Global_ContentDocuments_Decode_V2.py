import argparse
import gzip
import pathlib
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
    unit = 2 (uint16) or 4 (uint32)
    """
    count = min(max_count, len(blob) // unit)
    vals = []
    fmt = "<H" if unit == 2 else "<I"
    for i in range(count):
        off = i * unit
        val = struct.unpack_from(fmt, blob, off)[0]
        vals.append((off, val))
    return vals


def find_and_decompress_gzip(blob: bytes):
    """
    Search for a gzip header (1F 8B 08) in the file and try
    to decompress a valid gzip block from that offset.

    Returns (start_offset, end_offset, decompressed_bytes)
    or (None, None, None) if nothing is found.
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


def main():
    parser = argparse.ArgumentParser(
        description="Decode racbasicsamplefamily/Global_ContentDocuments.bin"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily/Global_ContentDocuments.bin",
        help="Path to Global_ContentDocuments.bin "
             "(default: racbasicsamplefamily/Global_ContentDocuments.bin)",
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
    safe_print("=== Header hexdump (first 0x50 bytes) ===")
    safe_print(hex_dump(blob[:0x50]))
    safe_print()

    safe_print("=== Header as 32-bit little endian integers ===")
    for off, val in parse_uints_le(blob[:0x50], unit=4, max_count=16):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    safe_print("=== Header as 16-bit little endian integers ===")
    for off, val in parse_uints_le(blob[:0x50], unit=2, max_count=32):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    if args.dump_hex:
        safe_print("=== Full hexdump of Global_ContentDocuments.bin ===")
        safe_print(hex_dump(blob))
        safe_print()

    # 2. Find gzip segment and decompress
    start, end, decomp = find_and_decompress_gzip(blob)
    if decomp is None:
        safe_print("No valid gzip segment found in Global_ContentDocuments.bin")
        return 0

    safe_print("=== Gzip segment found ===")
    safe_print(f"  start offset:      {start} (0x{start:04X})")
    safe_print(f"  end offset:        {end} (0x{end:04X})")
    safe_print(f"  compressed size:   {end - start} bytes")
    safe_print(f"  decompressed size: {len(decomp)} bytes")
    safe_print()

    # 3. Write decompressed data
    out_path = path.with_name("Global_ContentDocuments_decompressed.bin")
    out_path.write_bytes(decomp)
    safe_print(f"Decompressed data saved as: {out_path}")
    safe_print()

    # 4. Inspect structure of decompressed block
    safe_print("=== Decompressed hex (all bytes) ===")
    safe_print(hex_dump(decomp))
    safe_print()

    safe_print("=== Decompressed as 32-bit little endian integers ===")
    for off, val in parse_uints_le(decomp, unit=4, max_count=16):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    safe_print("=== Decompressed as 16-bit little endian integers ===")
    for off, val in parse_uints_le(decomp, unit=2, max_count=32):
        safe_print(f"  offset 0x{off:04X}: {val}")
    safe_print()

    safe_print(
        "Note: this block contains only binary values "
        "(no readable ASCII/UTF-16 strings); further interpretation "
        "requires knowledge of the internal Revit format."
    )
    safe_print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
