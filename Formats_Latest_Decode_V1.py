import argparse
import binascii
import pathlib
import re
import struct
import sys
import zlib

STDOUT_ENCODING = sys.stdout.encoding or "utf-8"


def safe_print(text: str = ""):
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode(STDOUT_ENCODING, errors="backslashreplace").decode(
            STDOUT_ENCODING, errors="backslashreplace"
        )
        print(safe)


def emit_lines(lines, output_lines):
    for line in lines:
        safe_print(line)
        output_lines.append(line)


def hexdump(data: bytes, max_bytes: int = 128, width: int = 16):
    data = data[:max_bytes]
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i : i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08X}: {hex_part:<47}  {ascii_part}")
    return lines


def parse_gzip_header(data: bytes):
    if len(data) < 10 or data[:2] != b"\x1f\x8b":
        raise ValueError("Not a gzip file")
    flags = data[3]
    pos = 10
    if flags & 0x04:
        if pos + 2 > len(data):
            raise ValueError("Invalid gzip header (FEXTRA)")
        xlen = struct.unpack_from("<H", data, pos)[0]
        pos += 2 + xlen
    if flags & 0x08:
        while pos < len(data) and data[pos] != 0:
            pos += 1
        pos += 1
    if flags & 0x10:
        while pos < len(data) and data[pos] != 0:
            pos += 1
        pos += 1
    if flags & 0x02:
        pos += 2
    return pos


def decompress_gzip_ignore_crc(data: bytes):
    start = parse_gzip_header(data)
    if len(data) < start + 8:
        raise ValueError("Truncated gzip stream")
    payload = data[start:-8]
    out = zlib.decompress(payload, wbits=-zlib.MAX_WBITS)
    return out


def extract_ascii_strings(data: bytes, min_len: int = 4):
    results = []
    current = bytearray()
    for b in data:
        if 32 <= b <= 126:
            current.append(b)
        else:
            if len(current) >= min_len:
                results.append(current.decode("ascii", errors="ignore"))
            current = bytearray()
    if len(current) >= min_len:
        results.append(current.decode("ascii", errors="ignore"))
    return results


def extract_utf16le_strings(data: bytes, min_len: int = 4):
    results = []
    current = []
    i = 0
    while i + 1 < len(data):
        ch = data[i]
        nul = data[i + 1]
        if 32 <= ch <= 126 and nul == 0:
            current.append(chr(ch))
        else:
            if len(current) >= min_len:
                results.append("".join(current))
            current = []
        i += 2
    if len(current) >= min_len:
        results.append("".join(current))
    return results


def find_length_prefixed_ascii(data: bytes, min_len: int = 3, max_len: int = 128):
    results = []
    seen = set()
    for i in range(0, len(data) - 2):
        length = data[i] | (data[i + 1] << 8)
        if length < min_len or length > max_len:
            continue
        end = i + 2 + length
        if end > len(data):
            continue
        chunk = data[i + 2 : end]
        if all(32 <= b <= 126 for b in chunk):
            s = chunk.decode("ascii", errors="ignore")
            if s not in seen:
                results.append((i, s))
                seen.add(s)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Decode Formats_Latest.bin from an RFA unpack."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=r"racbasicsamplefamily\Formats_Latest.bin",
        help="Path to Formats_Latest.bin",
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

    emit("Header hexdump (first 128 bytes):")
    emit_lines(hexdump(blob, max_bytes=128), output_lines)
    emit()

    try:
        data = decompress_gzip_ignore_crc(blob)
    except Exception as exc:
        emit(f"Decompression failed: {exc}")
        output_dir = pathlib.Path(__file__).resolve().parent
        output_path = output_dir / "Formats_Latest_V1_Readable.txt"
        output_path.write_text("\n".join(output_lines), encoding="utf-8")
        emit(f"Saved: {output_path}")
        return 1

    emit(f"Decompressed size: {len(data)} bytes")
    emit()

    emit("Decompressed hexdump (first 128 bytes):")
    emit_lines(hexdump(data, max_bytes=128), output_lines)
    emit()

    prefixed = find_length_prefixed_ascii(data, min_len=3, max_len=128)
    if prefixed:
        emit("Length-prefixed ASCII (u16 length) with offsets:")
        for off, s in prefixed:
            emit(f"  0x{off:06X}: {s}")
        emit()

    utf16_strings = extract_utf16le_strings(data, min_len=4)
    if utf16_strings:
        emit("UTF-16LE strings:")
        for s in utf16_strings:
            emit(f"  {s}")
        emit()

    ascii_strings = extract_ascii_strings(data, min_len=4)
    if ascii_strings:
        emit("ASCII strings:")
        for s in ascii_strings:
            emit(f"  {s}")
        emit()

    output_dir = pathlib.Path(__file__).resolve().parent
    output_path = output_dir / "Formats_Latest_V1_Readable.txt"
    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    emit(f"Saved: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
